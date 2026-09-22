# Usage Examples

## Check if a Service is Available

```python
import omni.kit.widget.nucleus_info

# Check if a specific service is available for a Nucleus URL
service_name = "NGSearch"
nucleus_url = "omniverse://localhost"
is_available = omni.kit.widget.nucleus_info.is_service_available(service_name, nucleus_url)
print(f"Is {service_name} service available on {nucleus_url}: {is_available}")
```
---

## Get Nucleus Services Synchronously

```python
import omni.kit.widget.nucleus_info

# Get services for a Nucleus URL synchronously
nucleus_url = "omniverse://localhost"
services = omni.kit.widget.nucleus_info.get_nucleus_services(nucleus_url)

if services:
    print(f"Found {len(services)} services for {nucleus_url}")
    for service in services:
        # Assuming the service object has a service_interface attribute with a name field
        print(f"Service: {service.service_interface.name}")
else:
    print(f"No services found for {nucleus_url} or services are being retrieved asynchronously")
```
---

## Working with Nucleus Services Asynchronously

```python
import omni.kit.widget.nucleus_info
import asyncio

async def nucleus_services_example():
    # Example 1: Get services for a single URL
    nucleus_url = "omniverse://localhost"
    print(f"Getting services for {nucleus_url}...")
    services = await omni.kit.widget.nucleus_info.get_nucleus_services_async(nucleus_url)
    
    if services:
        print(f"Found {len(services)} services")
        # Process some services here
    
    # Example 2: Check multiple URLs and specific services
    urls_to_check = ["omniverse://localhost", "omniverse://content"]
    services_to_check = ["NGSearch", "Otherservice"]
    
    for url in urls_to_check:
        # Check specific services availability
        for service_name in services_to_check:
            available = omni.kit.widget.nucleus_info.is_service_available(service_name, url)
            print(f"{service_name} on {url}: {'Available' if available else 'Not available'}")
        
        # Get and display all services
        all_services = await omni.kit.widget.nucleus_info.get_nucleus_services_async(url)
        if all_services:
            print(f"All services for {url}: {len(all_services)} found")
            for svc in all_services[:3]:  # Just show first 3 for brevity
                print(f"  - {svc.service_interface.name}")
        else:
            print(f"No services found for {url}")

# Run the async example
asyncio.ensure_future(nucleus_services_example())
```
