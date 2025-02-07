import subprocess            # Required
import sys                   # Required
import time                  # Required
import os                    # Required 

def usage(name):
    print(f"\nUsage:   python {name} model --local")
    print(f"\t python {name} model -l")
    print(f"\t python {name}\n")
    print("  model: The name of the model to use (default: deepseek-r1:1.5b)")
    print("  --local: Use the local version of ollama (default: False)")
    print("  -l: Use the local version of ollama (default: False)")

# Initialize variables
local = False
inputModel = 'deepseek-r1:1.5b'
num_ctx = 8192

def setup():
    global local
    global inputModel
    argc = len(sys.argv)
    if argc > 3:
        usage(sys.argv[0])
        sys.exit("\033[31m Too many arguments. \033[0m")
    
    # Check for unrecognized flags
    recognized_flags = {'--local', '-l'}
    for arg in sys.argv[1:]:
        if arg.startswith('-') and arg not in recognized_flags:
            usage(sys.argv[0])
            sys.exit(f"\033[31m Unrecognized flag: {arg} \033[0m")
    
    # Check if there is a --local option passed in (could be in a different order)
    if '--local' in sys.argv:
        local = True
        sys.argv.remove('--local')
    elif '-l' in sys.argv:
        local = True
        sys.argv.remove('-l')
    else:
        local = False

    # Set model to the input model
    if len(sys.argv) > 1:
        inputModel = sys.argv[1]

def setupLocal():
    # Command to upgrade pip
    print("\033[34m Upgrade pip... \033[0m")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)

    # Command to install ollama
    print("\033[34m Installing ollama... \033[0m")
    try:
        subprocess.run(["pip", "install", "ollama"], check=True)
    except subprocess.CalledProcessError as e:
        pass

    print("\033[34m Running ollama... \033[0m")
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.Popen(["ollama", "serve"], stdout=devnull, stderr=devnull)
    except subprocess.CalledProcessError as e:
        sys.exit("\033[31m Failed to run ollama. \033[0m")

    # Pull the model
    print("\033[34m Pulling the model... \033[0m")
    try:
        subprocess.run(["ollama", "pull", inputModel], check=True)
    except subprocess.CalledProcessError as e:
        print("\033[33m Could not pull the provided model. \033[0m")

def setupRemote():
    # Command to install requests
    print("\033[34m Installing requests... \033[0m")
    subprocess.run(["pip", "install", "requests"], check=True)

    # Stop the existing container if running
    print("\033[34m Stopping the existing container... \033[0m")
    try:
        subprocess.run(["docker", "stop", "ollama"], check=True)
    except subprocess.CalledProcessError as e:
        print("\033[33m No existing container to stop. \033[0m") 

    # Remove the existing container
    print("\033[34m Removing the existing container... \033[0m")
    try:
        subprocess.run(["docker", "rm", "ollama"], check=True)
    except subprocess.CalledProcessError as e:
        print("\033[33m No existing container to remove. \033[0m")

    # Run a new container
    print("\033[34m Starting a new container... \033[0m")
    try:
        subprocess.run([
        "docker", "run", "-d", "-v", "ollama:/root/.ollama", 
        "-p", "11434:11434", "--name", "ollama", "ollama/ollama"
        ], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit("\033[31m Failed to start the container. Ensure Docker is running. \033[0m")

    # Pull the model
    print(f"Pulling the model {inputModel}...")
    try:
        subprocess.run(["docker", "exec", "ollama", "ollama", "pull", inputModel], check=True)
    except:
        sys.exit(f"\033[31m Failed to pull the model: \t{inputModel} \n\033[0m Make sure you have the correct model name.")


def localTests():
    # Local version Packages
    from ollama import chat             
    from ollama import ChatResponse     

    # Local version tests

    # Test prompt
    print(" Running a test prompt with your model... \033[0m")
    start_time = time.time()
    try:
        response: ChatResponse = chat(model=inputModel, messages=[
                    {
                        'role': 'user',
                        'content': ' '
                    },
                ])
    except Exception as e:
        sys.exit(f"\033[31m Error: {e} \033[0m")
    end_time = time.time()
    print(f"\033[32m Test prompt completed in \033[0m{end_time - start_time:.2f} seconds")

def remoteTests(headers):
    # Remote version Packages
    import json                         
    import requests                     

    # Docker / Remote version tests 

    # Check if ollama container is running
    print("\033[34m Checking if the container is running... \033[0m")
    try:
        subprocess.run(["docker", "logs", "ollama"], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit("\033[31m Container is not running. \033[0m")

    # Notfiy the user that the container has started successfully
    print("\033[32m Container started successfully! \033[0m")
    print("\033[34m Connecting to the container... \033[0m")

    # Wait for the container to start
    time.sleep(3)

    # Check connection to ollama container
    try:
        response = requests.get('http://localhost:11434/api/version')
        if response.status_code == 200:
            version_info = json.loads(response.text)
    except:
        sys.exit('\033[31m Failed to connect to ollama. \033[0m')
    print("\033[32m Connected to ollama successfully! \n\033[0m")

    # Check the if a model is available
    print(" Checking available models...")    
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            # Debug
            # models = json.loads(response.text)
            # print("Available models:")
            # for model in models['models']:
            #     print(f"Name: {model['name']}")
            #     print(f"Model: {model['model']}")
            #     print(f"Modified At: {model['modified_at']}")
            #     print(f"Size: {model['size']} bytes")
            #     print(f"Digest: {model['digest']}")
            #     print("Details:")
            #     for key, value in model['details'].items():
            #         print(f"  {key}: {value}")
            models = json.loads(response.text)
            print(" Available models:")
            for model in models['models']:
                print(f"\033[0mName:\033[35m {model['name']} \033[0m")
                print(f"Model:\033[35m {model['model']} \033[0m")
                print(f"Size:\033[35m {model['size']} bytes \n\033[0m")
    except:
        sys.exit('\033[31m No models found. Try to pull manually. \033[0m')

    print("\033[36m Running a test prompt with your model... \n\033[0m")  
    start_time = time.time()
    try:
        response = requests.post(
                'http://localhost:11434/api/generate',
                headers=headers,
                data=json.dumps({
                    'model': inputModel,
                    'prompt': ' ',
                })
            )
    except:
        sys.exit('\033[31m Your model is not functioning or missing. Try to remove it and pull manually. \033[0m')
    end_time = time.time()
    print(f"\033[32m Test prompt completed in \033[0m{end_time - start_time:.2f} seconds")

def runRemote(headers):
    global num_ctx
    # Remote version Packages
    import json                         
    import requests                     

    try:
        inputMsg = input("\n\033[33mInput your prompt: \033[0m")
        print("🧠 Thinking...")
        response = requests.post(
            'http://localhost:11434/api/generate',
            headers=headers,
            data=json.dumps({
                'model': inputModel,
                'prompt': inputMsg,
                "options": {"num_ctx": num_ctx}
            })
        )
        print("🛑 Done!", end='')
        time.sleep(1)
        if response.status_code == 200:
            thinking = True
            # i = 1
            for line in response.text.splitlines():
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        # print(i,". ", data['response'], end='') # Debug
                        if '<think>' in data['response']:
                            thinking = True
                        elif'</think>' in data['response']:
                            thinking = False
                        else:
                            response = data['response']
                            if not thinking:
                                print(response, end='')
                except json.JSONDecodeError:
                    continue
                # i += 1
        else:
            print(f"\nRequest failed with status code {response.status_code}")
            print(f"Response: {response.text}")
        print()
    except requests.exceptions.RequestException as e:
        print(f"\n\033[31m Error: {e} \033[0m")
    except KeyboardInterrupt:
        sys.exit("\n\t\033[31m Exiting... \033[0m")
    except EOFError:
        pass

def runLocal():
    # Local version Packages
    from ollama import chat              
    from ollama import ChatResponse     
    import re                           
    try:
        inputMsg = input("\n\033[33mInput your prompt: \033[0m")
        print("🧠 Thinking...")
        try:
            response: ChatResponse = chat(model=inputModel, messages=[
                {
                    'role': 'user',
                    'content': inputMsg,
                    # 'options': {"num_ctx": 24576,
                    #             "num_predict": 8192}
                },
            ])
        except Exception as e:
            sys.exit(f"\033[31m Error: {e} \033[0m")
        print("🛑 Done! \n")
        time.sleep(1)
        content = re.sub(r'<think>.*?</think>', '', response.message.content, flags=re.DOTALL).strip()
        print(content)
    except KeyboardInterrupt:
        sys.exit("\n\t\033[31m Exiting... \033[0m")
    

def main():
    connected = False
    global local
    global inputModel

    setup()
    if local:
        setupLocal()
        print("\033[36m Running tests...")
        localTests()
    else:
        setupRemote()
        print("\033[36m Running tests...")
        headers = {
            'Content-Type': 'application/json'
        }
        remoteTests(headers)
        connected = True

    print("\033[32m All tests passed successfully. \033[0m")    

    print(f"\033[33m Using model:\t{inputModel} \033[0m")

    # Docker or Remote version
    while (connected == True) and (local == False):
        print('\n Press Ctrl+C to exit at any time.')
        runRemote(headers)

    # Local version with ollama installed
    while local:
        print('\n Press Ctrl+C to exit at any time.')
        runLocal()
        
if __name__ == '__main__':
    main()