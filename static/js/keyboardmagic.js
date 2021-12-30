// While not really a keyboard thing, this is a very useful utility for most pages
function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}
$(document).ready(function () {
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
  }

  //The help page
  if (winloc.includes("help") == false) {
    $(document).on("keydown", function (e) {
      if (e.key == "?") {
        window.location.href = "/help";
        return false;
      }
    });
  }

  //Go back to the last page when both shift and backspace are pressed
  $(document).on("keydown", function (e) {
    if (e.which == 8 && e.shiftKey) {
      window.history.back();
      return false;
    }
  });

  //When both control and q are pressed, go back to the main page
  $(document).on("keydown", function (e) {
    if (e.which == 81 && e.ctrlKey) {
      window.location.href = "/";
      return false;
    }
  });

  // If we are an a url that has "vid" in it, on space .play() the video
  if (winloc.includes("vid")) {
    const vid = player;
    const videoid = $(".vidid-holder").attr("id");
    // If we press the -> key, seek to 300 seconds
    $(document).on("keydown", function (e) {
      if (e.which == 39) {
        var vid = player;
        console.log(vid);
      }
    });
    // If the video is paused, play it when space is pressed. Otherwise, pause it
    $(document).on("keydown", function (e) {
      if (e.which == 32) {
        if (player.paused) {
          player.play();
          console.log("playing");
        } else {
          player.pause();
          console.log("paused");
        }
      }
    });
    // If the escape key is pressed, go back to the info page for that video id
    $(document).on("keydown", function (e) {
      if (e.which == 27) {
        window.location.href = "/info/" + videoid;
        return false;
      }
    });
  }

  // If we are on the info page, go to the video page when enter is pressed
  if (winloc.includes("info")) {
    $(document).on("keydown", function (e) {
      if (e.which == 13) {
        var lnk = $(".link").attr("link");
        window.location.href = "/vid/" + lnk;
        return false;
      }
    });
  }

  // If this is the home page, go to the search page when enter is pressed
  if (winloc == "http://127.0.0.1:8000/") {
    $(document).on("keydown", function (e) {
      if (e.which == 13) {
        window.location.href = "/search/";
        return false;
      }
    });
  }

  //as soon as we load the search page, focus on the search bar
  if (winloc.includes("search")) {
    $("#search").focus();
  }
});
