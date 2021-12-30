package main

import (
	"C"

	"github.com/lxn/win"
	"github.com/webview/webview"
)

//export webrunner
func webrunner() {
	debug := true
	w := webview.New(debug)
	defer w.Destroy()
	width := int(win.GetSystemMetrics(win.SM_CXSCREEN))
	height := int(win.GetSystemMetrics(win.SM_CYSCREEN))
	w.SetTitle("Videoplayer")
	w.SetSize(width, height, webview.HintNone)
	w.Navigate("http://127.0.0.1:8000/")
	w.Run()
}

func main() {}
