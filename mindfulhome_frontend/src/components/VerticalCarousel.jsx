import React from "react";
import "../styles/carousel.css";

export default function VerticalCarousel() {
    return (
        <div className="image-slider">
            <div className="image-slider-inner">
                <img src="/login_1.png" alt="1" />
                <img src="/login_2.png" alt="2" />
                <img src="/login_3.png" alt="3" />

                <img src="/login_1.png" alt="1 copy" />
            </div>
        </div>
    );
}
