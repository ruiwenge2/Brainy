function newInputField(){
  promptmodal("New Input Field", "Enter the name of the new input field:", ok="Create").then(name => {
    fetch("inputfields", {
      method:"PUT",
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
        location.reload();
      }
    });
  });
}

function renameInputField(){
  promptmodal("Rename Input Field", "Enter the name of the input field:", ok="Next").then(name => {
    promptmodal("Rename Input Field", "Enter the new name:", ok="Rename").then(newname => {
      fetch("inputfields", {
        method:"PATCH",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name: name,
          newname: newname
        })
      }).then(response => response.text()).then(response => {
        if(response != "Success"){
          alertmodal("", response);
        } else {
          location.reload();
        }
      });
    });
  });
}

function deleteInputField(){
  promptmodal("Delete Input Field", "Enter the name of the input field:", ok="Next").then(name => {
    confirmmodal("Delete Input Field", "Are you sure you want to delete this input field?", ok="Delete").then(newname => {
      fetch("inputfields", {
        method:"DELETE",
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
          location.reload();
        }
      });
    });
  });
}

function changePrivacy(){
  fetch("change", {
    method:"PATCH"
  }).then(response => response.text()).then(response => {
    if(response != "Success"){
      alertmodal("", response);
    } else {
      location.reload();
    }
  });
}

function endSurvey(){
  confirmmodal("End Survey", "Are you sure you want to end this survey? This cannot be undone.", ok="End").then(() => {
    fetch("change", {
      method:"PUT"
    }).then(response => response.text()).then(response => {
      if(response != "Success"){
        alertmodal("", response);
      } else {
        location.reload();
      }
    });
  });
}