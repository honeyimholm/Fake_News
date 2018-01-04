from Naked.toolshed.shell import execute_js, muterun_js

#NOTE: Must save file with UTF-8 encoding with BOM
#set text to translate here
text = "你好，世界!"
#translate script has automatic language detection
translate_script = '''  const translate = require('translate-api');
  let transText = \'''' + text + '''\';
  translate.getText(transText,{to: 'en'}).then(function(text){
    console.log(text);
  });'''
f = open('translate.js', 'w')
f.write(translate_script)
response = muterun_js('translate.js')
if response.exitcode == 0:
  print(str(response.stdout))
else:
  sys.stderr.write(response.stderr)