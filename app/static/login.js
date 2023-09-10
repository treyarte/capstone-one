$forkliftBtn = $(".guest-forklift-btn");
$stockerBtn = $(".guest-stocker-btn");

$emailField = $("#email");
$passwordField = $("#password");

/**
 * Auto fills the login for with guest stocker credentials
 * this is to allow recruiter to login without signing up
 */
function stockerLoginAutoFill() {
    $emailField.val("gueststocker@gmail.com");
    $passwordField.val("Thisisaguest1!");
}

/**
 * Auto fills the login for with guest focklift driver credentials
 * this is to allow recruiter to login without signing up
 */
function forkliftLoginAutoFill() {
    $emailField.val("guestforklift@gmail.com");
    $passwordField.val("Thisisaguest1!");
}

$forkliftBtn.on("click", forkliftLoginAutoFill);
$stockerBtn.on("click", stockerLoginAutoFill);