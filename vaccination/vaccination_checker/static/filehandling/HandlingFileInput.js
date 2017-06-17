if (window.File && window.FileReader && window.FormData) {
	var $inputField = $('#file');

	$inputField.on('change', function (e) {
		var file = e.target.files[0];

		if (file) {
			if (/^image\//i.test(file.type)) {
				readFile(file);
			} else {
				alert('Not a valid image!');
			}
		}
	});
} else {
	alert("File upload is not supported!");
}

function readFile(file) {
	var reader = new FileReader();

	//could resize photo here
	reader.onloadend = function () {
		processFile(reader.result, file.type);
	}

	reader.onerror = function () {
		alert('There was an error reading the file!');
	}

	reader.readAsDataURL(file);
}


//-----

function processFile(dataURL, fileType) {
	var maxWidth = 10000000;
	var maxHeight = 10000000;

	var image = new Image();
	image.src = dataURL;

	image.onload = function () {
		var width = image.width;
		var height = image.height;
		var shouldResize = (width > maxWidth) || (height > maxHeight);

		if (!shouldResize) {
			sendFile(dataURL);
			return;
		}

		var newWidth;
		var newHeight;

		if (width > height) {
			newHeight = height * (maxWidth / width);
			newWidth = maxWidth;
		} else {
			newWidth = width * (maxHeight / height);
			newHeight = maxHeight;
		}

		var canvas = document.createElement('canvas');

		canvas.width = newWidth;
		canvas.height = newHeight;

		var context = canvas.getContext('2d');

		context.drawImage(this, 0, 0, newWidth, newHeight);

		dataURL = canvas.toDataURL('image/jpeg');

		sendFile(dataURL);
	};

	image.onerror = function () {
		alert('There was an error processing your file!');
	};
}

//------


function sendFile(fileData) {
	var formData = new FormData();

	formData.append('imageData', fileData);

	$.ajax({
		type: 'POST',
		url: '/vaccination_checker/image_selector/',
		data: formData,
		contentType: false,
		processData: false,
		success: function (data) {
			if (data.success) {
				alert('Your file was successfully uploaded!');
			} else {
				alert('There was an error uploading your file!');
			}
		},
		error: function (data) {
			alert('There was an error uploading your file!');
		}
	});
}