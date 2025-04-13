import sys
print("Python path:", sys.path)

try:
    from openshot_rebuild import openshot
    print("OpenShot imported successfully:", openshot.OPENSHOT_VERSION_FULL)
    print("OpenShot capabilities:", {
        "Timeline available": hasattr(openshot, "Timeline"),
        "Frame available": hasattr(openshot, "Frame"),
        "Clip available": hasattr(openshot, "Clip")
    })
except Exception as e:
    print("Error importing OpenShot:", e)