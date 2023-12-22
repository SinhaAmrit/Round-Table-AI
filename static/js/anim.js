// Check if the user's device is not a mobile phone or a tablet
if (!/Mobi|Android/i.test(navigator.userAgent)) {
    // Execute the code for mouseFollower
    Shery.mouseFollower({
        skew: true,
        ease: "cubic-bezier(0.23, 1, 0.320, 1)",
        duration: 0.5,
    });
}
