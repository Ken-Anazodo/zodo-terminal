// Shop Now Items Section
$(document).ready(function(){
	$('.t-prod-container').on({
		mouseenter: function(){
			$(this).find('.shop-tag').css('display', 'flex')
		},

		mouseleave: function(){
			$(this).find('.shop-tag').css('display', 'none')
		}
	})
});


$(document).ready(function(){
	$('.front-sec-img-container').on({
		mouseenter: function(){
			$(this).find('.shop-tag1').css('display', 'flex')
		},

		mouseleave: function(){
			$(this).find('.shop-tag1').css('display', 'none')
		}
	})
});




// Display and remove Nav on small screen
document.addEventListener("DOMContentLoaded", function() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarMenu = document.querySelector('.full-screen-nav');

    navbarToggler.addEventListener('click', function() {
        // Toggle the open class for the burger icon
        navbarToggler.classList.toggle('open');
        
        // Toggle the visibility of the full-screen navigation menu
        navbarMenu.classList.toggle('show');

        // Check if the menu is open
        if (navbarMenu.classList.contains('show')) {
            // Prevent scrolling by hiding overflow on the body
            document.body.style.overflow = 'hidden';
        } else {
            // Enable scrolling by resetting overflow
            document.body.style.overflow = '';
        }
    });
});




// SEARCH HOVER EFFECT
$(document).ready(function(){
    // Delegated event handling
    $(document).on('mouseenter', 'table tr', function(){
        console.log("Mouse entered on row: ", $(this)); 
        $(this).css({
            'background-color': '#09090b',
            'color': '#ffff'
        });
		$(this).css({'font-family':'Helvetica', 'text-transform':'uppercase'})
        $(this).find('td a').css('color', '#ffff');
    });

    $(document).on('mouseleave', 'table tr', function(){
        console.log("Mouse left the row: ", $(this)); // Log the row
        $(this).css({
            'background-color': '#f6eddc',
            'color': '#09090b'
        });
		$(this).css({'font-family':'Helvetica Regular', 'text-transform':'capitalize'})
        $(this).find('td a').css('color', '#09090b');
    });
});




//cursor animation
document.addEventListener("DOMContentLoaded", (event) => {
		gsap.set(".ball", {xPercent: -50, yPercent: -50});

		let xTo = gsap.quickTo(".ball", "x", {duration: 0.6, ease: "power3"}),
			yTo = gsap.quickTo(".ball", "y", {duration: 0.6, ease: "power3"});

		window.addEventListener("mousemove", e => {
			xTo(e.clientX);
			yTo(e.clientY);
		});
});


//Mouse Hover Effect
// $(document).ready(function() {
//     $('.sec4-container').on({
//         mouseenter: function() {
//             // Select only the discovermore-cont within the hovered sec4-container
//             let discoverMore = $(this).find('.discovermore-cont');
// 			$(this).find('.ball').css({'display': 'none'});
            
//             // Set the initial position of the discovermore-cont
//             gsap.set(discoverMore, {xPercent: -50, yPercent: -50});

//             let xTo = gsap.quickTo(discoverMore, "x", {duration: 0.6, ease: "power3"}),
//                 yTo = gsap.quickTo(discoverMore, "y", {duration: 0.6, ease: "power3"});

//             // Attach the mousemove event to the window, but track the position of the hovered discovermore-cont
//             window.addEventListener("mousemove", moveHandler);

//             function moveHandler(e) {
//                 xTo(e.clientX);
//                 yTo(e.clientY);
//             }

//             // Store the moveHandler function so we can remove it later when leaving the container
//             $(this).data('moveHandler', moveHandler);
//         },

//         mouseleave: function() {
// 			$(this).find('.ball').css({'display': 'block'});
//             // Remove the mousemove event listener when leaving the sec4-container
//             let moveHandler = $(this).data('moveHandler');
//             window.removeEventListener("mousemove", moveHandler);

//             // Select only the discovermore-cont inside the container you're leaving
//             let discoverMore = $(this).find('.discovermore-cont');

//             // Animate the discovermore-cont back to its original position (center)
//             gsap.to(discoverMore, {x: 0, y: 0, duration: 0.6, ease: "power3"});
//         }
//     });
// });


