(function(){
  let key = document.createElement("input");
  key.name = "apikey";
  key.type = "hidden";
  key.value = "{{apikey}}";
  document.getElementById("form").appendChild(key);
})();