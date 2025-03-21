import requests
import yaml
import argparse
import json
import re

def fetch_wp_api_routes(base_url):
    """Fetches the available routes from the WordPress REST API."""
    print(f"Fetching API routes from {base_url}/wp-json")
    
    # Try the WordPress API discovery endpoint
    response = requests.get(f"{base_url}/wp-json")
    
    if response.status_code != 200:
        print(f"Failed to access {base_url}/wp-json. Status code: {response.status_code}")
        return {}
    
    try:
        data = response.json()
        if 'routes' in data:
            print(f"Found {len(data['routes'])} routes")
            return data['routes']
        else:
            print("No 'routes' key found in response.")
            return {}
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return {}

def process_arg_details(arg_name, arg_details):
    """Processes argument details to extract parameter information."""
    param = {
        "name": arg_name,
        "in": "query",
        "required": False,
        "schema": {
            "type": "string"
        },
        "description": ""
    }
    
    if isinstance(arg_details, dict):
        param_type = arg_details.get('type', 'string')
        
        # Handle different WordPress API parameter types
        if isinstance(param_type, list):
            # Some parameters can have multiple types
            param_type = param_type[0] if param_type else 'string'
        
        schema = {
            "type": param_type
        }
        
        # Handle enumerated values
        if 'enum' in arg_details:
            schema['enum'] = arg_details['enum']
        
        # Handle description
        description = arg_details.get('description', '')
        
        param.update({
            "required": arg_details.get('required', False),
            "schema": schema,
            "description": description
        })
    
    return param

def generate_openapi_spec(base_url, routes):
    """Generates an OpenAPI specification from the given routes."""
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "WordPress REST API",
            "version": "1.0.0",
            "description": "Auto-generated OpenAPI spec for WordPress REST API"
        },
        "servers": [{"url": base_url}],
        "paths": {}
    }
    
    for route, details in routes.items():
        # Clean up route path to make it OpenAPI compatible
        # Replace WordPress regex patterns with OpenAPI parameters
        path = route.replace('/wp/v2', '')  # Remove namespace prefix
        
        # Replace WordPress regex patterns with OpenAPI parameters
        path = re.sub(r'\(\?P<([^>]+)>\[\\d\]\+\)', r'/{{\1}}', path)
        path = re.sub(r'\(\?P<([^>]+)>[^)]+\)', r'/{{\1}}', path)
        
        if not path.startswith('/'):
            path = '/' + path
            
        path_item = {}
        
        if isinstance(details, dict) and 'endpoints' in details:
            for endpoint in details.get('endpoints', []):
                for method in endpoint.get('methods', []):
                    method = method.lower()
                    parameters = []
                    
                    # Extract path parameters from the route
                    path_params = re.findall(r'{([^}]+)}', path)
                    for param_name in path_params:
                        parameters.append({
                            "name": param_name,
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            },
                            "description": f"Path parameter: {param_name}"
                        })
                    
                    # Process args if they exist
                    args = endpoint.get('args', {})
                    if isinstance(args, dict):
                        for arg_name, arg_details in args.items():
                            # Skip path parameters that are already added
                            if arg_name not in path_params:
                                param = process_arg_details(arg_name, arg_details)
                                parameters.append(param)
                    
                    path_item[method] = {
                        "summary": f"{method.upper()} {path}",
                        "description": details.get('description', ''),
                        "parameters": parameters,
                        "responses": {
                            "200": {
                                "description": "Successful response"
                            },
                            "400": {
                                "description": "Bad request"
                            },
                            "401": {
                                "description": "Unauthorized"
                            },
                            "404": {
                                "description": "Resource not found"
                            }
                        }
                    }
            
            if path_item:  # Only add non-empty path items
                openapi_spec["paths"][path] = path_item
    
    return openapi_spec

def main():
    parser = argparse.ArgumentParser(description="Generate OpenAPI spec from WordPress REST API.")
    parser.add_argument("base_url", help="Base URL of the WordPress site (e.g., https://example.com)")
    parser.add_argument("-o", "--output", default="wordpress_openapi.yaml", help="Output file name for the OpenAPI spec")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    try:
        # Remove trailing slash from base_url if present
        base_url = args.base_url.rstrip('/')
        
        routes = fetch_wp_api_routes(base_url)
        
        if args.verbose:
            print(f"Found routes: {json.dumps(list(routes.keys()), indent=2)}")
        
        openapi_spec = generate_openapi_spec(base_url, routes)
        
        # Check if we have any paths
        if not openapi_spec["paths"]:
            print("Warning: No API paths were extracted. The OpenAPI specification will be empty.")
        
        with open(args.output, "w") as file:
            yaml.dump(openapi_spec, file, sort_keys=False)
        
        print(f"OpenAPI specification has been generated and saved to {args.output}")
        print(f"Found {len(openapi_spec['paths'])} API paths")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching API routes: {e}")
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()