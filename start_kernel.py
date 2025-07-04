from federacja.core.kernel import FederationKernel

if __name__ == "__main__":
  config ={
    "kernel_name": "FederationKernel",
    "kernel_version": "1.0.0",
    "kernel_description": "Kernel Federacji",
    "kernel_author": "Wilson",
    "kernel_license": "MIT",
    "kernel_dependencies": "test"
  }
  kernel = FederationKernel(config)