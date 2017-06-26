from Naked.toolshed.shell import execute_js

#NOTE: Must save file with UTF-8 encoding with BOM
#set text to translate here
text = "测试"
#translate script has automatic language detection
translate_script = '''const translate = require('google-translate-api');
translate(''' + text  + ''', {to: 'en'}).then(res => {
    console.log(res.text);
    //=> I speak English
    console.log(res.from.language.iso);
    //=> nl
}).catch(err => {
    console.error(err);
});'''

f = open('translate.js', 'w')
f.write(translate_script)
f.write("test!")
success = execute_js('translate.js')
print success