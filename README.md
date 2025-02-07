# How to run  
_\* python & python3 are interchangeable_  

In your command line or terminal use:  
- python main.py model --local  
-- or --  
- python main.py model -l  
-- or --  
- python main.py model

_\* pulls models using ollama based on their naming  
  Ex: deepseek-v3_  

### Examples:
- python main.py deepseek-r1:7b --local  
(Runs ollama and model locally)  
- python3 main.py deepseek-coder-v2  
(Runs ollama and model in docker container)  

* **The --local or -l flag is optional**
  - With --local or -l: ollama and the model locally on your system
  - Without any flags: run the ollama docker image with chosen model

# Notes

When using a larger input, like pasting lots of code, while running locally you may need to use the modelfile to patch the context limit of the input model. 
- Step 1. Pull the model manually using: ollama pull model
- Step 2. Run this command: ollama create model-patch -f modelfile
- Step 3. Use the new model name "model-patch" the next time you run
### Example:
  - ollama pull deepseek-coder-v2
  - ollama create deepseek-coder-v2-patch -f modelfile
  - python main.py deepseek-coder-v2-patch -l

# How it should look:
![image](https://github.com/user-attachments/assets/da8af09c-cd6e-4442-8a76-a54f0d81aca7)
