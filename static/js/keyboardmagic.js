var winloc = this.location.href;
if (winloc.includes("search")) {
  console.log("search");
  $(document).on("keydown", function (e) {
    if (e.which == 32) {
      $("#search").focus();
      $(".selected").addClass("presel").removeClass("selected");
    }
    if (e.which == 27) {
      $("#search").blur();
      $(".presel").addClass("selected").removeClass("presel");
    }
  });
} else {
  console.log("not search");
}
