# Variables

---

As of Maestro v. 0.1.6 it is now possible to use variables in the configuration file to keep sensitive information out of VCS. At this time variables are only available in the VALUE portion of the `variables` portion of the config file.   

If you'd like to use variables the syntax is simple.

```
"variables": {
    "key1": "${var.value1}",
    "key2": "${var.value2}"
}
```

Then simply append the `--var` flag onto your command line when running any of Maestro's actions.  

Example:  
- `maestro run example.json --var value1 mySecretValue --var value2 mySecondSecretValue`  