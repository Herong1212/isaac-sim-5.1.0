import omni.ui as ui
import carb.settings as settings

# Copied from kit\source\extensions\omni.iray.settings.core\omni\iray\settings\core\widgets\heatma_bar.py with minimum modifications
# TODO Consider optimizing _fill_color_bar with precomputed texture.
# Currently it does width x height pixels compute on update callback that should be mostly identical on every re-evaluation

class PhotometricHeatmapBarWidget:
    def __init__(self, parent_widget, width = 400, height = 20, steps = 4, type = "illumination"):
        self._settings = settings.get_settings()

        if type == "illumination":
            self._unit = "Lux"
            self._rangeMinSetting = "/rtx/pathtracing/illuminanceMin"
            self._rangeMaxSetting = "/rtx/pathtracing/illuminanceMax"
            self._rangeUserMinSetting = "/rtx/pathtracing/illuminanceUserMin"
            self._rangeUserMaxSetting = "/rtx/pathtracing/illuminanceUserMax"
            self._valueSetting = "/rtx/pathtracing/illuminanceVal"
            self._rangeAutoRangeSetting = "/rtx/pathtracing/illuminanceAutoRange"
        elif type == "lumination":
            self._unit = "Nits"
            self._rangeMinSetting = "/rtx/pathtracing/luminanceMin"
            self._rangeMaxSetting = "/rtx/pathtracing/luminanceMax"
            self._rangeUserMinSetting = "/rtx/pathtracing/luminanceUserMin"
            self._rangeUserMaxSetting = "/rtx/pathtracing/luminanceUserMax"
            self._valueSetting = "/rtx/pathtracing/luminanceVal"
            self._rangeAutoRangeSetting = "/rtx/pathtracing/luminanceAutoRange"
        else:
            raise Exception("Unsupported heatmap type " + type)

        self._parent_widget = parent_widget
        self._width = width
        self._height = height
        self._labels = []
        self._steps = steps
        
        self._photometric_min = 0.0
        self._photometric_max = 0.0
        self._photometric_value = 0.0
        self._photometric_value_str = "0.0 " + self._unit
        self._photometric_value_fraction = 0.0
        
        self._update_values()
        
        with ui.Frame():
            with ui.VStack():
                p = ui.Percent((100/self._steps) * 0.5)
                
                # current photometric value
                with ui.HStack(height=20):
                    
                    self._photometric_value_spacer_l = ui.Spacer()
                    self._photometric_value_label = ui.Label("0.0", alignment=ui.Alignment.CENTER, width=ui.Percent(p*2))
                    self._photometric_value_spacer_r = ui.Spacer()
                    
                    self._update_value()
 
                # color bar
                with ui.HStack(height=20):
                
                    ui.Spacer(width=ui.Percent(p))
                    
                    pixels = [0] * width * height * 4
                    self._color_bar = ui.ByteImageProvider()
                    self._color_bar.set_bytes_data(pixels, [width, height])
                    
                    ui.ImageWithProvider(self._color_bar, fill_policy=ui.IwpFillPolicy.IWP_STRETCH)
                    self._fill_color_bar(self._photometric_value_fraction)
                    
                    ui.Spacer(width=ui.Percent(p))
                    
                # ticks bar
                with ui.HStack(height=10):   
                    ui.Spacer(width=ui.Percent(p))                
                    self._ticks_bar = ui.ByteImageProvider()
                    self._ticks_bar.set_bytes_data(pixels, [width, height])
                    
                    ui.ImageWithProvider(self._ticks_bar,
                                         fill_policy=ui.IwpFillPolicy.IWP_STRETCH,
                                         )
                    self._fill_ticks_bar(0.0)
                        
                    ui.Spacer(width=ui.Percent(p))

                with ui.HStack(height=20):
                    for i in range(steps):
                        self._labels.append(ui.Label(str(i), alignment=ui.Alignment.CENTER))
                self._update_legend()

        self._settings.subscribe_to_node_change_events(self._rangeMinSetting, self._update_cb)
        self._settings.subscribe_to_node_change_events(self._rangeMaxSetting, self._update_cb)
        self._settings.subscribe_to_node_change_events(self._rangeUserMinSetting, self._update_cb)
        self._settings.subscribe_to_node_change_events(self._rangeUserMaxSetting, self._update_cb)
        self._settings.subscribe_to_node_change_events(self._rangeAutoRangeSetting, self._update_cb)
        self._settings.subscribe_to_node_change_events(self._valueSetting, self._update_cb)

    def _fill_ticks_bar(self, val):
        pixels = [0] * self._width * self._height * 4
        l = int(self._width * val)
        r = int((self._width) / (self._steps - 1))
        for x in range(self._width):
            for y in range(self._height):
                p = y * self._width * 4 + x * 4
                if x % r < 2 or x >= self._width - 2:
                    pixels[p + 0] = 255
                    pixels[p + 1] = 255
                    pixels[p + 2] = 255
                    pixels[p + 3] = 255
        self._ticks_bar.set_bytes_data(pixels, [self._width, self._height])

    def _fill_color_bar(self, val):
        def get_color(t):
            c = [255,255,255]

            if t < 0.25:
                c[0] = 0
                c[1] = int(4.0 * t * 255)
            elif t < 0.5:
                c[0] = 0
                c[2] = int((1.0 + 4.0 * (0.25 * 1.0 - t)) * 255)
            elif t < 0.75:
                c[0] = int(4.0 * (t - 0.5) * 255)
                c[2] = 0
            else:
                c[1] = int((1.0 + 4.0 * (0.75 - t)) * 255)
                c[2] = 0
            return c
            
        pixels = [255] * self._width * self._height * 4
        l = int(self._width * val)
        for x in range(self._width):
            for y in range(self._height):
                p = y * self._width * 4 + x * 4
                if x >= l-1 and x <= l+1:
                    c = [255] * 4
                else:     
                    c = get_color(x / self._width)
                pixels[p + 0] = c[0]
                pixels[p + 1] = c[1]
                pixels[p + 2] = c[2]

        self._color_bar.set_bytes_data(pixels, [self._width, self._height])

    def _update_values(self):
        # avoid unnecessary redraw as it can tank the frame rate
        requireRedraw = False

        newPhotometricMin = float(self._settings.get(self._get_range_min_name()) or 0.0)
        if newPhotometricMin != self._photometric_min:
            requireRedraw = True
        self._photometric_min = newPhotometricMin

        newPhotometricMax = float(self._settings.get(self._get_range_max_name()) or 10000.0)
        if newPhotometricMax <= 0.0:
            newPhotometricMax = 10000
        if newPhotometricMax != self._photometric_max:
            requireRedraw = True
        self._photometric_max = newPhotometricMax

        newPhotometricValueStr = settings.get_settings().get(self._valueSetting) or "0.0 " + self._unit
        if newPhotometricValueStr != self._photometric_value_str:
            requireRedraw = True
        self._photometric_value_str = newPhotometricValueStr
        try:
            self._photometric_value = float(self._photometric_value_str.split()[0])
        except:
            self._photometric_value = 0.0
        d = self._photometric_max - self._photometric_min
        if d == 0.0:
            d = 1.0
        if self._photometric_value > self._photometric_max:# can happen with user-range
            self._photometric_value = self._photometric_max
        if self._photometric_value < self._photometric_min:# can happen with user-range
            self._photometric_value = self._photometric_min
        self._photometric_value_fraction = (self._photometric_value - self._photometric_min) / d

        return requireRedraw

    def _update_cb(self, item, event_type):
        requireRedraw = self._update_values()
        self._update_legend()
        self._update_value()
        if requireRedraw:
            self._fill_color_bar(self._photometric_value_fraction)

    def _update_legend(self):
        incr = (self._photometric_max - self._photometric_min) / (self._steps - 1)
        for i in range(self._steps):
            self._labels[i].text = "%.1f" % (self._photometric_min + i * incr)

    def _update_value(self):

        w1 = 1/ (1 /self._steps + 1)

        self._photometric_value_label.text = self._photometric_value_str

        p = 0#ui.Percent((100/self._steps) * 0.5)

        p0 = self._photometric_value_fraction * w1 * 100
        if p0-p <= 0:
            p0 = 0
        self._photometric_value_spacer_l.width = ui.Percent(p0-p)

    def _get_range_min_name(self):
        auto_range = settings.get_settings().get(self._rangeAutoRangeSetting)
        if auto_range:
            return self._rangeMinSetting
        return self._rangeUserMinSetting

    def _get_range_max_name(self):
        auto_range = settings.get_settings().get(self._rangeAutoRangeSetting)
        if auto_range:
            return self._rangeMaxSetting
        return self._rangeUserMaxSetting

    def __del__(self):
        self._settings.unsubscribe_to_change_events(self._update_cb)
