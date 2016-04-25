var selectedUniqueKey;

$(document).ready(function() 
{ 
	$(".advancedTable").DataTable();

	$("#updateDB").click(function(){
		$.ajax({
	        url:  "updateDB",
	        type: "POST"
	    });
	})

	$("#addAlert").click(function(){
		var username = $("#username").text();
		var attribute = $("#attribute").val();
		var comparison = $("#comparison").val();
		var value = $("#value").val();
		var data = "username=" + username + "&attribute=" + attribute + "&comparison=" + comparison + "&value=" + value;
		$.ajax({
	        url:  "addAlert",
	        type: "POST",
	        data: data
	    });
	    location.reload();
	});

	$("#addUser").click(function(){
		var fname = $("#fname").val();
		var lname = $("#lname").val();
		var username = $("#newUsername").val();
		var password = $("#newPassword").val();
		var email = $("#email").val();
		var permissions = $("#permissions").val();
		var data = "fname=" + fname + "&lname=" + lname + "&username=" + username + "&password=" + password + "&email=" + email + "&permissions=" + permissions;
		$.ajax({
	        url:  "addUser",
	        type: "POST",
	        data: data
	    });
	    location.reload();
	});

	$("#toggleAlertHelp").click(function(){
		$("#alertHelp").toggleClass("hide");
	});

	$("#editEmail").click(function(){
		$("#alertHelp").removeClass("hide");
	});

	$(".deleteAlert").click(function(){
		selectedUniqueKey = this.id;
	});

	$("#confirmDelete").click(function(){
		var data = 'uniqueKey=' + selectedUniqueKey;
		$.ajax({
	        url:  "deleteAlert",
	        type: "POST",
	        data: data
	    });
	    location.reload();
	});



} 
);