function getXMLHttpRequest() {

	var xhr = null;

	if (window.XMLHttpRequest || window.ActiveXObject) {
		if (window.ActiveXObject) {
			try {
				xhr = new ActiveXObject("Msxml2.XMLHTTP");
			} catch(e) {
				xhr = new ActiveXObject("Microsoft.XMLHTTP");
			}
		} else {
			xhr = new XMLHttpRequest();
		}
	} else {
		alert("Votre navigateur ne supporte pas l'objet XMLHTTPRequest...");
		return null;
	}

	return xhr;
}

function request(method, url, callback, data=null) {

	xhr = getXMLHttpRequest();

	xhr.onreadystatechange = function() {

		if(xhr.readyState==4) {

			if(xhr.status==200 || xhr.status==0) {

				return callback(xhr.responseText);
			}
			else {

				console.log("ERROR ["+xhr.status+"]");
				return;
			}

		}
	}

	xhr.open(method, url, false);
	xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhr.send(data);

}
