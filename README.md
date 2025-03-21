# WordPress to OpenAPI Generator

A Python tool that automatically generates OpenAPI specifications by crawling WordPress REST API endpoints. This tool is particularly useful for security researchers, penetration testers, and developers who need to map WordPress site APIs for testing or integration purposes.

## Features

- Automatically discovers WordPress REST API endpoints
- Converts WordPress API routes to OpenAPI 3.0 specification format
- Handles complex WordPress route patterns with regex
- Properly extracts parameter information and details
- Converts WordPress-style parameter patterns to OpenAPI path parameters
- Generates a clean YAML output file compatible with tools like Swagger UI or Burp Suite

## Installation

### Prerequisites

- Python 3.6+
- pipx

### Install dependencies

```bash
pipx install requests pyyaml
```

## Usage

```bash
python generate_openapi.py https://example.com [-o output_file.yaml] [-v]
```

### Parameters

- `base_url`: The base URL of the WordPress site (required)
- `-o, --output`: Output file name for the OpenAPI spec (default: wordpress_openapi.yaml)
- `-v, --verbose`: Enable verbose output

## Example

```bash
python generate_openapi.py https://example.com -o sei_api.yaml -v
```

This will:
1. Fetch all available routes from the WordPress REST API at the specified URL
2. Generate an OpenAPI 3.0 specification
3. Save the specification to the specified output file

## Use Cases

- **Security Testing**: Map WordPress APIs to discover potential attack vectors
- **API Integration**: Generate client code based on the OpenAPI specification
- **Burp Suite Import**: Load the generated spec into Burp Suite for automated scanning
- **Documentation**: Create interactive API documentation using Swagger UI

## Limitations

- Requires the WordPress site to have the REST API enabled and accessible
- May not capture all custom endpoints added by plugins if they don't follow standard WordPress API patterns
- Authentication requirements for protected endpoints must be handled separately

## Importing to Burp Suite

1. Generate the OpenAPI specification using this tool
2. In Burp Suite, go to Extensions → OpenAPI/Swagger Parser
3. Import the generated YAML file
4. The parser will create a site map with all the discovered endpoints

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
