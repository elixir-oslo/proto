var ctx;
var LinkLocation = [];
var canvas;

//function for creating a box
//x = x position of the box
//y = y position of the box
//size = height of the box
//text = an array that contains the the text to be printed inside the box, the first item is the large subtitle
//subs = the positions of the smaller subtitles in the text array, leave it empty and there won't be any smaller subtitles
//llength = the length of each string in the form of an array [title, smallerTitle, text]
//color = the color of the box
function createBox(ctx,x,y,size,text,links,subs,llength,color)
{
	var maxWidth = 0;
	var maxHeight = size;
	var titleHeight = 0;
	for (i = 0; i < text.length; i++)
	{
		if(text[i].length > 15)
		{
			maxWidth = 10;
			maxHeight += 22;
		}
		else if((text[i].length/llength[2]) > maxWidth)
		{
			maxWidth = text[i].length/llength[2];
		}
	}
	maxWidth = maxWidth * 4 + 80;
	roundedRect(ctx,x,y,maxWidth,maxHeight,15,color);
	var floors = rectTitle(ctx,x-8,y+5,maxWidth,text[0],llength[0]);
	lines(ctx,x+5,y+38+floors*15,maxWidth-10,"#CCCCCC");
	for (k = 1; k < text.length; k++)
	{
		if(subs.indexOf(k) > -1)
		{
			floors += rectSubs(ctx,x+5,y+60+floors*13,maxWidth,text[k],llength[1]);	
		}
		else
		{
			floors += rectText(ctx,x+5,y+60+floors*13,text[k],links[k],llength[2],color);		
		}
	}
}

//function to create a rounded rectangle
function roundedRect(ctx,x,y,width,height,radius,color)
{
	ctx.beginPath();
	ctx.strokeStyle = "#000000";
	ctx.moveTo(x,y+radius);
	ctx.lineTo(x,y+height-radius);
	ctx.arcTo(x,y+height,x+radius,y+height,radius);
	ctx.lineTo(x+width-radius,y+height);
	ctx.arcTo(x+width,y+height,x+width,y+height-radius,radius);
	ctx.lineTo(x+width,y+radius);
	ctx.arcTo(x+width,y,x+width-radius,y,radius);
	ctx.lineTo(x+radius,y);
	ctx.arcTo(x,y,x,y+radius,radius);
	ctx.fillStyle = color;
	ctx.fill();
	ctx.stroke();
}

//function for splitting the text between lines
function splittingText(ctx,wholeText,numberSplit)
{
	var splitText = wholeText.split(" ");
	var sepString = new Array;
	var counter = 0;
	var floor = 0;
	
	sepString[floor] = "";
	for(i = 0; i < splitText.length; i++)
	{
		counter += splitText[i].length;
		if(counter <= numberSplit)
		{
			sepString[floor] += splitText[i] + " ";
		}
		else
		{
			floor += 1;
			counter = splitText[i].length;
			sepString[floor] = splitText[i] + " ";
		}
	}

	return sepString;
}

//function to write bigger titles
function rectTitle(ctx,x,y,width,text,llength)
{
	var splitText = splittingText(ctx,text,llength);
	for(i = 0; i < splitText.length; i++)
	{
		ctx.beginPath();
		ctx.font = "bold 11px Arial";
		ctx.fillStyle = '#000005';
		ctx.textAlign = "center";
		if(splitText[i] != undefined)
		{
			ctx.fillText(splitText[i],x+width/2+10, y+20+(i*16));
		}
	}

	return splitText.length-1;
}

//function to write smaller titles
function rectSubs(ctx,x,y,width,text,llength)
{
	var splitText = splittingText(ctx,text,llength);
	for(i = 0; i < splitText.length; i++)
	{
		ctx.beginPath();
		ctx.font = "bold 10px Arial";
		ctx.fillStyle = '#000005';
		ctx.textAlign = "center";
		if(splitText[i] != undefined)
		{
			ctx.fillText(splitText[i],x+width/2-5, y+(i*15));
		}
	}

	return splitText.length;
}

//fucntion to write lines of text
function rectText(ctx,x,y,text,links,llength,color)
{
	var splitText = splittingText(ctx,text,llength);
	var oneExtra = 1;
	var linkX = [];
	var linkY = [];
	var linkWidth = [];

	for(i = 0; i < splitText.length; i++)
	{
		ctx.beginPath();
		ctx.font = "9px Arial";
		ctx.strokeStyle = "#000000";
		ctx.textAlign = "left";
		if(splitText[i] != undefined)
		{
			ctx.fillText(splitText[i],x+3,y+(i*14));
			linkX.push(x+3);
			linkY.push(y+(i*14)+2);
			linkWidth.push(ctx.measureText(splitText[i]).width);
		}
		else
		{
			oneExtra = 0;
		}
	}
	LinkLocation.push([links,linkX,linkY,linkWidth,color,false]);
	
	return splitText.length + 1;
}

//function for drawing a line
function lines(ctx,x,y,length,color)
{
	ctx.beginPath();
	ctx.moveTo(x,y);
	ctx.lineTo(x+length,y);
	ctx.strokeStyle = color;
	ctx.stroke();
}

//function for drawing an arrow
function arrow(ctx,fromx,fromy,tox,toy)
{
	var headlen = 10;   // length of head in pixels
    var angle = Math.atan2(toy-fromy,tox-fromx);
    ctx.beginPath();
    ctx.moveTo(fromx, fromy);
    ctx.lineTo(tox, toy);
    ctx.lineTo(tox-headlen*Math.cos(angle-Math.PI/6),toy-headlen*Math.sin(angle-Math.PI/6));
    ctx.moveTo(tox, toy);
    ctx.lineTo(tox-headlen*Math.cos(angle+Math.PI/6),toy-headlen*Math.sin(angle+Math.PI/6));
	ctx.stroke()
}

//function for adding an Event Listener to the canvas
function canvasListening(theCanvas)
{
	canvas = theCanvas;
	theCanvas.addEventListener("mousemove", on_mousemove, false);
	theCanvas.addEventListener("click", on_click, false);
}


//function to check if the mouse is over the link, change cursor style and underline
function on_mousemove (ev) 
{
	var x, y;
	var pointer;
	overLink = false;
	var isChromium = window.chrome,
    winNav = window.navigator,
    vendorName = winNav.vendor,
    isOpera = winNav.userAgent.indexOf("OPR") > -1,
    isIEedge = winNav.userAgent.indexOf("Edge") > -1,
    isIOSChrome = winNav.userAgent.match("CriOS");
	var rect = canvas.getBoundingClientRect();
	var element = document.body;

	// Get the mouse position relative to the canvas element.
	/*if (ev.layerX || ev.layerX) { //for firefox
		x = ev.layerX - rect.left;
		y = ev.layerY - rect.top;
	}*/

	if(isIOSChrome){
	   // is Google Chrome on IOS
		x = ev.layerX;
		y = ev.layerY;
	} else if(isChromium !== null && isChromium !== undefined && vendorName === "Google Inc." && isOpera == false && isIEedge == false) {
	   // is Google Chrome
		x = ev.layerX;
		y = ev.layerY;
	} else { 
	   // not Google Chrome 
		x = ev.layerX - rect.left;
		y = ev.layerY - rect.top;
	}

	x-=canvas.offsetLeft - rect.left - element.scrollLeft;
	y-=canvas.offsetTop - rect.top - element.scrollTop;

	for(i = 0; i < LinkLocation.length; i++)
	{
		linkX = LinkLocation[i][1][0];
		linkY = LinkLocation[i][2][0];
		linkXlength = LinkLocation[i][1].length;
		linkWidth = LinkLocation[i][3][linkXlength-1];
		linkHeight = 20;
		//is the mouse over the link?
		if(x>=linkX && x <= (linkX + linkWidth) &&
		   y<=linkY && y>= (linkY-linkHeight))
		{
			LinkLocation[i][5]=true;
			overLink = true;
			for(j = 0; j < LinkLocation[i][1].length; j++)
			{
				lines(ctx,LinkLocation[i][1][j],LinkLocation[i][2][j],LinkLocation[i][3][j],"#000000");
			}
		}
		else
		{
			document.body.style.cursor = "";
			LinkLocation[i][5]=false;
			for(j = 0; j < LinkLocation[i][1].length; j++)
			{
				lines(ctx,LinkLocation[i][1][j],LinkLocation[i][2][j],LinkLocation[i][3][j],LinkLocation[i][4]);
			}
		}
		if(overLink)
		{
			document.body.style.cursor = "pointer";
		}
	}
}
 
//function to check if the link has been clicked, go to link
function on_click(e) {
	for(i = 0; i < LinkLocation.length; i++)
	{
		isLink = LinkLocation[i][5];
		if (isLink)  {
			window.location = LinkLocation[i][0];
		}
	}
}