function searchResultsPopulate(pageStart, pageSize){
    var xhr = new XMLHttpRequest();
    var query = document.getElementById('query').innerHTML;
    xhr.open("GET", "/search/getpg/?page_start=" + pageStart.toString() + "&page_size=" + pageSize.toString() + "&query=" + query);
    xhr.onreadystatechange = function(){
        if(xhr.readyState === 4){
          if(xhr.status === 200){
            var loading = document.getElementById('loading-items');
            loading.parentNode.removeChild(loading);
            var response = JSON.parse(xhr.responseText);
            var parent = document.getElementById('container')
            var i;
            for (i = 0; i < response.length; i++){
                var div = document.createElement('div');
                if(Math.random() > 0.5){
                    div.classList.add("cus-col-2");
                }
                else{
                    div.classList.add("cus-col-1");
                }
                div.classList.add("brick");
                div.innerHTML =
                    `<div class="fit-img">
                        <div class="content">
                            <a href="/profile/` + response[i].uploader + `/all/img-view?selected=` + response[i].id + `">
                                <div class="small-thumb-cover" style="background-image: url(` + response[i].url + `)"></div>
                            </a>
                        </div>
                    </div>`
                parent.appendChild(div);
                document.getElementById("loadCount").innerHTML = (parseInt(document.getElementById("loadCount").innerHTML) + 1).toString()
            }


            $(function() {
              var wall = new Freewall("#container");
              wall.reset({
                    selector: '.brick',
                    animate: true,
                    cellW: 160,
                    cellH: 160,
                    fixSize: null,
                    onResize: function() {
                        wall.fitWidth();
                    }
              });
              wall.fitWidth();
            });

        }


          else{
            alert("Image fetching failed");
          }
        }
    };
    xhr.send();
}

function onScroll(){
    var query = document.getElementById('query').innerHTML;
    if($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
               imagePopulate(parseInt(document.getElementById("loadCount").innerHTML), 50, query)
           }
}

// window.onload = function() {
//   imagePopulate();
// };