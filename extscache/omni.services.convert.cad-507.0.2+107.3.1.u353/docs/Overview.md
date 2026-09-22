# Overview

`omni.services.convert.cad` is a Kit services extension that provides a service for batch conversion of CAD files to USD using various CAD converter extensions. This service extension leverages the underlying CAD converter capabilities to convert files such as SLDPRT, DGN, JT, and other supported CAD formats to USD format. Refer to [omni.kit.converter.cad](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.cad/latest/Overview.html#formats-and-features-supported) docs for list of all supported CAD files.

Upon loading, it registers with the CAD Converter service, allowing other extensions and external processes to utilize its conversion capabilities through a standardized API interface.

## About

The CAD Converter Service Extension provides an easy-to-use API to call into the CAD conversion service for converting various CAD file formats to USD.

## Usage

The CAD Converter Service Extension can be used in several ways:

1. **Direct API Calls**: Call the service directly from Python code or other extensions
2. **Batch Processing**: Use for automated conversion of multiple CAD files
3. **Integration**: Integrate with other Omniverse services and extensions
4. **Container Deployment**: Deploy as a service in CAD containers for scalable processing
5. **Farm Setup**: Use with Omniverse TAAS and Farm for distributed processing

The service provides a robust and flexible solution for converting various CAD file formats to USD, making it easier to work with different CAD types in the Omniverse ecosystem.

For detailed usage instructions, see the [Usage Guide](Usage.md).

## Supported File Formats

The CAD Converter Service supports conversion from the following file formats to USD:
- **DGN** (.dgn)
- **JT** (.jt)
- **HOOPS Supported Formats**: Various CAD formats supported by HOOPS Exchange

> Note: For a complete list of supported CAD files, refer to [omni.kit.converter.cad](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.cad/latest/Overview.html#formats-and-features-supported) documentation.

## CAD CONVERTER SERVICE REQUEST FORMAT

The CAD Converter Service accepts requests in JSON format with the following structure:

### Request Arguments:

#### Required Arguments:

**import_path**
- **Description**: Full path to the source CAD file to convert
- **Data Format**: string
- **Example**: `"/path/to/model.sldprt"`

**output_path**
- **Description**: Full path to the output USD file
- **Data Format**: string
- **Example**: `"/path/to/output/model.usd"`

#### Optional Arguments:

**converter_options**
- **Description**: JSON object containing conversion configuration options
- **Data Format**: object
- **Default Value**: `{}`
- **Example**: `{ "bInstancing": true }`
- **Note**: This option takes precedence over the config_path option

**config_path**
- **Description**: Path to the JSON config file (Optional and deprecated)
- **Data Format**: string
- **Default Value**: `""`
- **Example**: `"/path/to/config.json"`

## Sample Request Examples

### Minimal Conversion Request:

```json
{
  "import_path": "/ANCHOR.sldprt",
  "output_path": "/tmp/testing/ANCHOR.usd"
}
```

### Basic Conversion Request:

```json
{
  "import_path": "/ANCHOR.sldprt",
  "output_path": "/tmp/testing/ANCHOR.usd",
  "converter_options": { "bInstancing": true }
}
```

### Conversion with Config File:

```json
{
  "import_path": "/tmp/input_file.dgn",
  "output_path": "/tmp/output_file.usd",
  "config_path": "/tmp/sample_config.json"
}
```

### Advanced Conversion Request:

```json
{
  "import_path": "/path/to/complex_model.sldprt",
  "output_path": "/path/to/output/complex_model.usd",
  "converter_options": {
    "bInstancing": true,
    "bOptimize": true,
    "bConvertHidden": false,
    "dMetersPerUnit": 1.0,
    "iUpAxis": 1
  }
}
```

## CONVERTER-SPECIFIC OPTIONS AND CONFIGURATION

Conversion options are configured by supplying a JSON object in the `converter_options` parameter. The available configuration options depend on the specific CAD converter being used.

### Converter-Specific Configuration Options:

**HOOPS Core Converter**: Refer to [omni.kit.converter.hoops_core](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.hoops_core/latest/Overview.html#json-converter-settings) for configuration options.

**JT Core Converter**: Refer to [omni.kit.converter.jt_core](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.jt_core/latest/Overview.html#json-converter-settings) for configuration options.

**DGN Core Converter**: Refer to [omni.kit.converter.dgn_core](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.dgn_core/latest/Overview.html#json-converter-settings) for configuration options.

## Detailed Usage Instructions

For comprehensive usage instructions, including:

- [Setting up your extension as a Kit Service](Usage.md#10-how-to-set-your-extension-up-as-a-kit-service)
- [Using the service in Omniverse Applications](Usage.md#20-how-to-use-a-service)
- [Running batch jobs locally via CLI](Usage.md#30-how-to-run-batch-jobs-locally-via-cli)

Please refer to the [Usage Guide](Usage.md).

## Licensing Terms of Use and Third-Party Notices
The `omni.services.convert.cad` and related CAD converter Extensions are Omniverse Core Extensions.
Do not redistribute or sublicense without express permission or agreement.
Please read the [Omniverse License Agreements](https://docs.omniverse.nvidia.com/extensions/latest/common/NVIDIA_Omniverse_License_Agreement.html) for detailed license information.
