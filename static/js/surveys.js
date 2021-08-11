function newSurvey(){
  promptmodal("New Survey", "Enter the name of the survey:", ok="Create").then(name => {
    if(!name){
      newSurvey();
      return;
    }
    fetch("/newsurvey", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: name
      })
    }).then(response => response.text()).then(response => {
      if(response != "Success"){
        alertmodal("", response);
      } else {
        location.href = `${username}/${name}/dashboard`;
      }
    });
  });
}

function rename(name){
  promptmodal("Rename Survey", "Enter a new name for this survey:", ok="Rename").then(newname => {
    if(!newname){
      rename(name);
      return;
    }
    fetch(`/${username}/${name}/rename`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: newname
      })
    }).then(response => response.text()).then(response => {
      if(response != "Success"){
        alertmodal("", response);
      } else {
        location.reload();
      }
    });
  });
}

function del(name){
  confirmmodal("Delete Survey", "Are you sure you want to delete this survey?", ok="Delete").then(() => {
    fetch(`/${username}/${name}/delete`, {
      method: "POST"
    }).then(response => response.text()).then(response => {
      if(response != "Success"){
        alertmodal("", response);
      } else {
        location.reload();
      }
    });
  });
}

function search(){
  var value = document.getElementById("search").value;
  for(let i of document.querySelectorAll(".surveyname")){
    if(i.innerHTML.includes(value)){
      i.parentElement.style.display = "inline-block";
    } else {
      i.parentElement.style.display = "none";
    }
  }
}