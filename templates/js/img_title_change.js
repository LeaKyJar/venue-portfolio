$('#carousel-custom').on('slid.bs.carousel', function (e) {
    var index = $(e.target).find(".active").html();
    document.getElementById('img-title').innerHTML = "- " + e.relatedTarget.id.toUpperCase() + " -"
});