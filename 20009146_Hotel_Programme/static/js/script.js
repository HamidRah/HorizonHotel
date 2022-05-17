// Hamidur Rahman: 20009146
const navBtn = document.getElementById('nav-btn');
const cancelBtn = document.getElementById('cancel-btn');
const sideNav = document.getElementById('sidenav');
const modal = document.getElementById('modal');

navBtn.addEventListener("click", function(){
    sideNav.classList.add('show');
    modal.classList.add('showModal');
});

cancelBtn.addEventListener('click', function(){
    sideNav.classList.remove('show');
    modal.classList.remove('showModal');
});

window.addEventListener('click', function(event){
    if(event.target === modal){
        sideNav.classList.remove('show');
        modal.classList.remove('showModal');
    }
});

// Date Validation

function setCheckoutMinimum(){
    var checkIn = new Date(document.getElementById("checkin").value);
    var year = checkIn.getFullYear();
    var month = checkIn.getMonth() + 1;
    var day = checkIn.getDate() + 1;           
    if (month < 10) {
        month = '0' + month; 
    }
    if (day < 10) {
        day = '0' + day; 
    }
    var checkoutMin = year + '-' + month + '-' + day;

    console.log(checkoutMin);
    document.getElementById("checkout").min = checkoutMin;
}


function initialDate(){
    var today=new Date();
    var year = today.getFullYear();
    var month = today.getMonth() + 1;
    var day = today.getDate();           
    if (month < 10) {
        month = '0' + month; 
    }
    if (day < 10) {
        day = '0' + day; 
    }
    today = year + '-' + month + '-' + day;
    console.log("Today");
    console.log(today);       
    document.getElementById("checkin").min = today;            
}

function maxCheckin(){
    var today=new Date();
    var year = today.getFullYear();
    var month = today.getMonth() + 4;
    var day = today.getDate();           
    if (month < 10) {
        month = '0' + month; 
    }
    if (day < 10) {
        day = '0' + day; 
    }
    today = year + '-' + month + '-' + day;
    console.log("Today");
    console.log(today);       
    document.getElementById("checkin").max = today;            
}

function timeDelta(){
    var checkIn = new Date(document.getElementById("checkin").value);
    var year = checkIn.getFullYear();
    var month = checkIn.getMonth() + 2;
    var day = checkIn.getDate();           
    if (month < 10) {
        month = '0' + month; 
    }
    if (day < 10) {
        day = '0' + day; 
    }
    var checkoutMax = year + '-' + month + '-' + day;

    console.log(checkoutMax);
    document.getElementById("checkout").max = checkoutMax;               
}



window.addEventListener('load', function(){
    initialDate();
});

window.addEventListener('load', function(){
    maxCheckin();
});

window.addEventListener('change', function(){
    setCheckoutMinimum();
});

window.addEventListener('change', function(){
    timeDelta();
});



