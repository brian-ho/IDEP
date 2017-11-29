//check if browser supports file api and filereader features
if (window.File && window.FileReader && window.FileList && window.Blob) {

  // Load data
  var csv_full;
  $.ajax({
      async: false,
      url: 'data/kl_full.csv',
      success: function(data) {csv_full = data;}
  });
  // Initialize array of image IDs and index
  // var ids = $.csv.toArray(csv).map(Number);
  var results = Papa.parse(csv_full, {header: true,});
  var data = results['data'];
  var length = data.length;

  console.log("KL DATASET LODADED: "+ data.length);
  var ind = 0

  function nextImage(){
      ind = (length+ind+1) % length;
      renderTemplate();
  }

  function prevImage(){
      ind = (length+ind-1) % length;
      renderTemplate();
    }

  function renderTemplate(){
      console.log(ind);
      the_url = 'images/'+data[ind]['id']+'.jpg';
      $('#preview').html("<img src='"+the_url+"' />");
      $('#text').html(data[ind]['text']);
      $('#id').html(data[ind]['id']);
  }
/*
   //this is not completely neccesary, just a nice function I found to make the file size format friendlier
	//http://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable
	function humanFileSize(bytes, si) {
	    var thresh = si ? 1000 : 1024;
	    if(bytes < thresh) return bytes + ' B';
	    var units = si ? ['kB','MB','GB','TB','PB','EB','ZB','YB'] : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
	    var u = -1;
	    do {
	        bytes /= thresh;
	        ++u;
	    } while(bytes >= thresh);
	    return bytes.toFixed(1)+' '+units[u];
	}

  //this function is called when the input loads an image
	function renderImage(file){
		var reader = new FileReader();
		reader.onload = function(event){
			the_url = event.target.result
      //of course using a template library like handlebars.js is a better solution than just inserting a string
			$('#preview').html("<img src='"+the_url+"' />")
			$('#name').html(file.name)
			$('#size').html(humanFileSize(file.size, "MB"))
			$('#type').html(file.type)
		}
    //when the file is read it triggers the onload event above.
		reader.readAsDataURL(file);
	}

  //watch for change on the
	$( "#the-photo-file-field" ).change(function() {
		console.log("photo file has been chosen")
		//grab the first image in the fileList
		//in this example we are only loading one file.
		console.log(this.files[0].size)
		renderImage(this.files[0])
	});
*/

nextImage()

} else {
  alert('The File APIs are not fully supported in this browser.');
}
