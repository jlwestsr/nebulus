import docker
import logging

# Configure logger
logger = logging.getLogger(__name__)


def run_code_in_sandbox(language: str, code: str, timeout: int = 10) -> str:
    """
    Executes code in a secure, ephemeral Docker container.

    Args:
        language (str): The programming language (e.g., 'python').
        code (str): The code snippet to execute.
        timeout (int): Execution timeout in seconds.

    Returns:
        str: The stdout/stderr output or error message.
    """
    if language.lower() not in ["python", "python3"]:
        return "Error: Only Python execution is currently supported."

    client = docker.from_env()
    container = None

    try:
        # Pull the image if not present (using a lightweight python image)
        image = "python:3.11-slim"

        # Run the container
        # - remove=True: Cleanup container after exit
        # - network_disabled=True: No internet access for security
        # - mem_limit: Restrict memory usage
        # - cpu_quota: Restrict CPU usage (optional)
        container = client.containers.run(
            image,
            command=["python", "-c", code],
            remove=True,
            network_disabled=True,
            mem_limit="128m",
            stderr=True,
            stdout=True,
            detach=False,  # Wait for execution
        )

        return container.decode("utf-8")

    except docker.errors.ContainerError as e:
        # Container exited with non-zero exit code
        return f"Execution Error:\n{e.stderr.decode('utf-8') if e.stderr else 'Unknown error'}"

    except docker.errors.ImageNotFound:
        return f"Error: Sandbox image '{image}' not found and could not be pulled."

    except docker.errors.APIError as e:
        return f"Docker API Error: {str(e)}"

    except Exception as e:
        return f"System Error: {str(e)}"


if __name__ == "__main__":
    # Simple test
    print(run_code_in_sandbox("python", "print('Hello form Sandbox')"))
