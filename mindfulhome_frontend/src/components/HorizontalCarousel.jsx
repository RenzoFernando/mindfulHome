import React, { useState, useEffect, useRef } from 'react';
import '../styles/horizontal-carousel.css';

const HorizontalCarousel = ({ children }) => {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const containerRef = useRef(null);
    const childrenCount = React.Children.count(children);

    const goToSlide = (index) => {
        if (isTransitioning || index === currentIndex) return;
        
        setIsTransitioning(true);
        setCurrentIndex(index);
        
        setTimeout(() => {
            setIsTransitioning(false);
        }, 500);
    };

    // Función para siguiente slide
    const nextSlide = () => {
        if (isTransitioning) return;
        const nextIndex = (currentIndex + 1) % childrenCount;
        goToSlide(nextIndex);
    };

    // Función para slide anterior
    const prevSlide = () => {
        if (isTransitioning) return;
        const prevIndex = (currentIndex - 1 + childrenCount) % childrenCount;
        goToSlide(prevIndex);
    };

    // Manejar teclado para navegación
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'ArrowLeft') {
                prevSlide();
            } else if (e.key === 'ArrowRight') {
                nextSlide();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [currentIndex, isTransitioning]);

    if (childrenCount === 0) {
        return (
            <div className="horizontal-carousel">
                <div className="carousel-empty">
                    <p>No hay slides para mostrar</p>
                </div>
            </div>
        );
    }

    return (
        <div className="horizontal-carousel">
            <div 
                className="carousel-container"
                ref={containerRef}
            >
                <div 
                    className="carousel-track"
                    style={{
                        transform: `translateX(-${currentIndex * 100}%)`,
                        transition: isTransitioning ? 'transform 0.5s ease-in-out' : 'none'
                    }}
                >
                    {React.Children.map(children, (child, index) => (
                        <div className="carousel-slide" key={index}>
                            {child}
                        </div>
                    ))}
                </div>
            </div>

            {/* Puntos indicadores */}
            {childrenCount > 1 && (
                <div className="carousel-dots">
                    {Array.from({ length: childrenCount }).map((_, index) => (
                        <button
                            key={index}
                            className={`carousel-dot ${index === currentIndex ? 'active' : ''}`}
                            onClick={() => goToSlide(index)}
                            aria-label={`Ir al slide ${index + 1}`}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default HorizontalCarousel;