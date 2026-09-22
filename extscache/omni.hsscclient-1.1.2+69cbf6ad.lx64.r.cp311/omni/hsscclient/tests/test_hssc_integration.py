import csv
import json
import os
import pathlib
import shutil
import socket
import subprocess
import time
from collections import abc

import carb
import omni.kit.test
import toml
from omni.kit.core.tests.test_base import KitLaunchTest
from omni.ui.tests.compare_utils import CompareMetric, compare


def deep_update(sdict, udict):
    """Update nested-dict sdict with also-nested-dict udict, only where udict has keys set"""
    for k, v in udict.items():
        if isinstance(v, abc.Mapping) and v:
            sdict[k] = deep_update(sdict.get(k, {}), v)
        else:
            sdict[k] = udict[k]
    return sdict


def keychain(default, dictionary, keys):
    """Take iterable `keys` and dictionary-of-dictionaries, and keep resolving until you run out of keys. If we fail to look up, return default. Otherwise, return final value"""
    try:
        for k in keys:
            dictionary = dictionary[k]
        return dictionary
    except KeyError:
        return default


class Memcached:
    """Class to manage memcached server shard
    TODO: Add multi-platform support."""

    def __init__(self, objsize, poolsize, threads):
        """Ensure memcached is installed, then start with:
        - `objsize`: maximum allowed object size
        - `poolsize`: total memory pool size
        - `threads`: # of threads

        This will try to pick port 11211 and probe for a for a failed one."""

        self.objsize = objsize
        self.poolsize = poolsize
        self.threads = threads
        self.ip = "127.0.0.1"
        tokens = carb.tokens.get_tokens_interface()
        thisdir = pathlib.Path(__file__).resolve().parents[7]
        testlibs = thisdir.joinpath(tokens.resolve("${platform}/${config}/testlibs/"))
        self.binpath = os.path.realpath(testlibs.joinpath(tokens.resolve("memcached/${platform}/${config}/memcached")))
        self.start()

    def binary(self):
        """Memcached binary."""
        return self.binpath

    def start(self):
        """Start memcached, probing for free port. Will give up after 50 tries."""
        code = 71  # code 71 is "port was busy"
        tries = 0
        port = 11211
        while code == 71:
            args = [self.binary(), "-p", str(port), "-I", self.objsize, "-m", self.poolsize, "-t", str(self.threads)]
            proc = subprocess.Popen(args)  # noqa: PLR1732
            time.sleep(1)
            code = proc.poll()
            if code != 71:
                break
            tries += 1
            port += 1
            if tries > 50:
                raise RuntimeError("Can't start memcached!")
        assert proc.poll() is None

        self.proc = proc  # Hang on to process context
        print(f"Started memcached @ port {port}")
        self.port = port  # hand on to successful port

    @staticmethod
    def flush(ip, port):
        """This sends a `flush_all` to the memcached server at ip:port"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(bytes("flush_all\r\n", "ascii"))
        reply = ""
        dat = s.recv(4096)
        reply = str(dat, "utf-8")
        assert reply == "OK\r\n"
        s.close()

    def flush_this(self):
        """Member version of above"""
        Memcached.flush(self.ip, self.port)

    def stop(self):
        """Kills memcached process."""
        self.proc.kill()

    @staticmethod
    def format_uris(uris):
        """Format URIs in list-of (ip, port) tuples to pass to kit."""
        return ",".join((f"memcache://{ip}:{port}" for (ip, port) in uris))


def get_hssc_log(logfile):
    """Read CSV file at `logfile`, returning dict of columns (lists)"""
    with open(logfile, mode="r", encoding="utf-8") as fp:
        reader = csv.reader(fp, delimiter=",")
        items = [(s.strip(), []) for s in next(reader)]
        for li in reader:
            for idx, it in enumerate(li):
                items[idx][1].append(it)
        return {field[0]: field[1] for field in items}


scenes = [
    ("testtex", pathlib.Path(__file__).resolve().parents[0].joinpath("data/testtex/testtex.usda")),
]


async def compare_images(golden_path: str, capture_path: str, diff_path: str, threshold: float):
    """Compare golden image with test image and provide diff image MSE match status."""

    mse = compare(
        pathlib.Path(golden_path),
        pathlib.Path(capture_path),
        pathlib.Path(diff_path),
        cmp_metric=CompareMetric.MEAN_ERROR_SQUARED,
    )

    matches_golden_image = mse <= threshold

    if matches_golden_image:
        carb.log_info(f"MSE of ref {golden_path} with capture {capture_path} is {mse} (PASSES {threshold})")
    else:
        carb.log_info(
            f"MSE of ref {golden_path} with capture {capture_path} is {mse} (FAILS {threshold}, diff image in {diff_path})"
        )

    return mse, matches_golden_image


class TestHSSCIntegration(KitLaunchTest):  # pragma: no cover
    """Main test harness for HSS$. Starts up memcached shards and runs series of tests"""

    async def setUp(self):
        """Initialize shards"""
        self.shards = [Memcached("1024m", "101024", 16), Memcached("1024m", "101024", 16)]
        await super().setUp()

    async def tearDown(self):
        """Take down shards"""
        await super().tearDown()
        for s in self.shards:
            s.stop()

    def flush_all(self):
        """Clear shard states"""
        for s in self.shards:
            s.flush_this()

    async def runkit(self, config):
        """Start kit with given args, with particular knobs in `config`
        Returns a dict with information about output directories & logs."""
        base_args = [
            "--no-audio",
            "--enable",
            "omni.kit.uiapp",
            "--enable",
            "omni.hydra.rtx",
            "--enable",
            "omni.usd",
            "--enable",
            "omni.kit.window.extensions",
            "--enable",
            "omni.kit.viewport.utility",
            "--enable",
            "omni.kit.viewport.bundle",
            "--enable",
            "omni.kit.viewport.rtx",
            "--enable",
            "omni.kit.renderer.capture",
            "--enable",
            "omni.mdl",
            "--enable",
            "omni.mdl.neuraylib",
            "--enable",
            "omni.hydra.engine.stats",
            "--/crashreporter/skipOldDumpUpload=true",
            "--/crashreporter/gatherUserStory=0",  # don't pop up the GUI on crash
            "--/app/skipOldDumpUpload=true",
            "--/app/renderer/sleepMsOutOfFocus=0",
            "--/rtx/ecoMode/enabled=false",
            "--/app/asyncRendering=false",
            "--/foundation/verifyOsVersion/enabled=false",
            "--/rtx/verifyDriverVersion/enabled=false",
            "--/persistent/renderer/startupMessageDisplayed=true",
            "--no-window",
            "--portable",
            "--/app/window/hideUi=true",
            "--/app/docks/disabled=true",
            "--/app/viewport/forceHideFps=true",
            "--/persistent/app/viewport/displayOptions=1024",
            "--/app/viewport/show/lights=false",
            "--/app/viewport/show/audio=false",
            "--/app/viewport/show/camera=false",
            "--/app/viewport/grid/enabled=false",
            "--/app/window/scaleToMonitor=false",
            "--/app/window/dpiScaleOverride=1.0",
            "--/rtx/materialDb/syncLoads=true",
            "--/omni.kit.plugin/syncUsdLoads=true",
            "--/rtx/hydra/materialSyncLoads=true",
            "--/rtx-transient/dlssg/enabled=false",  # OM-97205: Disable DLSS-G for now globally, so L40 tests will all pass. DLSS-G tests will have to enable it
        ]

        # Create directory, (delete if already exists)
        output_dir = config["test"]["resdir"]
        try:
            os.makedirs(output_dir)
        except FileExistsError:
            shutil.rmtree(output_dir)
            os.makedirs(output_dir)

        run_res = {}
        args = base_args[:]
        args += [
            f"--/app/renderer/resolution/width={config['kit']['resolution'][0]}",
            f"--/app/renderer/resolution/height={config['kit']['resolution'][1]}",
        ]
        run_res["kit_log"] = os.path.join(output_dir, "kit.log")
        args += [f"--/log/file={run_res['kit_log']}"]

        if "hssc_config" in config:
            args += [
                "--enable",
                "omni.hsscclient",
                "--enable",
                "omni.ujitso.client",
                f"--/UJITSO/datastore/hsscUri={Memcached.format_uris(config['hssc_config']['uris'])}",
                "--/UJITSO/enabled=true",
            ]
            if "log" in config["hssc_config"]:
                run_res["hssc_log"] = os.path.join(output_dir, config["hssc_config"]["log"])
                args += [f"--/UJITSO/datastore/hsscLogFile={run_res['hssc_log']}"]
            if keychain(False, config, ("hssc_config", "preflush")):
                for s in config["hssc_config"]["uris"]:
                    Memcached.flush(*s)

            geometry = keychain(False, config, ("ujitso", "geometry"))
            textures = keychain(False, config, ("ujitso", "textures"))
            remote = keychain(False, config, ("ujitso", "remote"))

            args += [f"--/UJITSO/geometry={str(geometry).lower()}"]
            args += [f"--/UJITSO/textures={str(textures).lower()}"]
            args += [f"--/UJITSO/datastore/useRemoteCache={str(remote).lower()}"]

        run_res["load_usd_output"] = output_dir
        extra_args = [
            "load_usd.py",
            f'--stage {config["test"]["usd_url"]}',
            "--output_folder",
            f"{output_dir}",
            "--screenshot_pause",
            "10",
        ]

        root = pathlib.Path(__file__).resolve().parent
        path = os.path.join(root, "load_usd.py")
        with open(path, mode="r", encoding="utf-8") as fp:
            script = fp.read()
        await self._run_kit_with_script(script, args=args, script_extra_args=" " + " ".join(extra_args), timeout=600)
        return run_res

    def default_config(self):
        """Default params for tests"""
        config = """[kit]
resolution = [ 1280, 720]

[hssc_config]
log = "hssclog.csv"
preflush = false

[ujitso]
textures = true
geometry = true
remote = true

[test]
"""
        return toml.loads(config)

    @staticmethod
    def get_load_time(resdict):
        """Return load time from json file indicated by dict"""
        with open(os.path.join(resdict["load_usd_output"], "stats.json"), mode="r", encoding="utf-8") as fp:
            stats = json.load(fp)

        return stats["load_time"]

    async def run_warm_cold(self, name, usd, overrides=None, imagecomp=False, checkwarmfaster=False, lossy=False):
        """Load `usd` twice; the expectation is that the caches are 'cold' to start with, and then 'warm' the second time."""
        if overrides is None:
            overrides = {}
        self.flush_all()
        config = self.default_config()
        config = deep_update(config, overrides)
        config["test"]["usd_url"] = usd
        config["hssc_config"]["uris"] = [(s.ip, s.port) for s in self.shards]

        if imagecomp:
            hssc_config = config["hssc_config"]
            ujitso_config = config["ujitso"]
            del config["hssc_config"]
            del config["ujitso"]

            config["test"]["resdir"] = os.path.join(omni.kit.test.get_test_output_path(), f"ref_{name}")
            res = await self.runkit(config)

            ref_image = os.path.join(config["test"]["resdir"], "screenshot.png")
            # _ref_load = self.get_load_time(res)

            config["hssc_config"] = hssc_config
            config["ujitso"] = ujitso_config

        with self.subTest(f"cold {name}"):
            config["test"]["resdir"] = os.path.join(omni.kit.test.get_test_output_path(), f"cold_{name}")

            res = await self.runkit(config)
            if imagecomp:
                cold_image = os.path.join(config["test"]["resdir"], "screenshot.png")
                _mse, matches = await compare_images(
                    ref_image, cold_image, os.path.join(config["test"]["resdir"], "refdiff.png"), 0.01
                )
                self.assertTrue(matches)

            log = get_hssc_log(res["hssc_log"])
            self.assertGreater(
                len(log["id"]), 5
            )  # This is a punt; we should do more detailed investation. For now, anything in the log indicates that we are talking to the HSS$
            cold_load = self.get_load_time(res)

        with self.subTest(f"warm {name}"):
            config["test"]["resdir"] = os.path.join(omni.kit.test.get_test_output_path(), f"warm_{name}")

            res = await self.runkit(config)

            if imagecomp:
                warm_image = os.path.join(config["test"]["resdir"], "screenshot.png")
                _mse, matches = await compare_images(
                    ref_image, warm_image, os.path.join(config["test"]["resdir"], "refdiff.png"), 0.01
                )
                self.assertTrue(matches)

            log = get_hssc_log(res["hssc_log"])
            self.assertGreater(
                len(log["id"]), 5
            )  # This is a punt; we should do more detailed investation. For now, anything in the log indicates that we are talking to the HSS$

            warm_load = self.get_load_time(res)
            if checkwarmfaster:  # Ideally, we could mark this as a "not critical" test, since it could be noisy.
                self.assertGreater(cold_load, warm_load)

        if lossy:
            with self.subTest(f"warm lossy {name}"):
                config["test"]["resdir"] = os.path.join(omni.kit.test.get_test_output_path(), f"warm_lossy_{name}")
                self.shards[0].flush_this()
                res = await self.runkit(config)

                if imagecomp:
                    warm_image = os.path.join(config["test"]["resdir"], "screenshot.png")
                    _mse, matches = await compare_images(
                        ref_image, warm_image, os.path.join(config["test"]["resdir"], "refdiff.png"), 0.01
                    )
                    self.assertTrue(matches)

                log = get_hssc_log(res["hssc_log"])
                self.assertGreater(
                    len(log["id"]), 5
                )  # This is a punt; we should do more detailed investation. For now, anything in the log indicates that we are talking to the HSS$

                # we don't check for faster 'warm' times since we expect to pay for having to rebuild things

    async def test_tex_remote_image(self):
        odict = {
            "ujitso": {
                "geometry": False,
                "textures": True,
                "remote": True,
            }
        }
        for name, usd in scenes:
            name = f"{name}_tex"
            with self.subTest(name):
                await self.run_warm_cold(name, usd, odict, imagecomp=True, lossy=False)

    async def test_tex_remote_image_lossy(self):
        odict = {
            "ujitso": {
                "geometry": False,
                "textures": True,
                "remote": True,
            }
        }
        for name, usd in scenes:
            name = f"{name}_tex_lossy"
            with self.subTest(name):
                await self.run_warm_cold(name, usd, odict, imagecomp=True, lossy=True)
