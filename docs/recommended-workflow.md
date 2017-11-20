# Recommended workflow  

---

This is the recommended workflow for using Maestro:  

### Update your Lambda configuration  
- Run `maestro update-config example.json`  

### Update your Lambda code to $LATEST  
- Run `maestro update-code --no_pub example.json`  

### Publish a new version of your lambda code  
- Run `maestro publish example.json`  

### Update your alias to the new version you've published  
- Run `maestro update-alias example.json`  


---

## Why?  

1. Run update config. This is to prepare the lambda configuration for any changes necessary for new code.  
2. Run update-code --no_pub. This is to push the new code up to $LATEST, let's us test it while our production traffic/events continue to operate on an alias.  
3. Run publish. This is to publish a new version of the code. Each time you have new working code it's recommended to publish a version. This is useful so you have a working version if you need to roll your alias back to old code. We'll point our production alias to this version.  
4. Run update-alias. This is to update the alias to the version we published with the 'publish action'

---

## Lambda best practices  

### Your events or traffic should always be served via an alias.  
- This allows you to test new code on $LATEST without breaking your lambda.  

### Every time you push new working code you should publish a version.
- This allows you to have a number of previous working versions, so you can easily rollback

