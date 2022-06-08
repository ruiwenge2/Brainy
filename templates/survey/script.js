(function(){
  let key = document.createElement("input");
  key.name = "apikey";
  key.type = "hidden";
  key.value = "";
  {% for i in apikey %}key.value += "{{i}}";
  {% endfor %}document.getElementById("form").appendChild(key);
})();
