# Refactor to do  

---

- Create schema for passing to "main.py" this should be comprised of CLI args and configuration from the json  
- refactor the main function to make sense to people reading it, it should not be 200 lines  
- move the main function to main.py  
- use maestro.py as the entry point, should take json config data and CLI and transform it using schema from config_shema.py  
- Move colors to it's own class, it's annoying to see at the top of each file
- Make sure all logging has colors
- Rename files to be more clear
- Double check inline docs
