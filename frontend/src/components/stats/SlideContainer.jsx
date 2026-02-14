export default function SlideContainer({ slideIndex, totalSlides, children }) {
  return (
    <div className="fixed inset-0 flex flex-col bg-background text-foreground">
      <div className="flex flex-1 items-center justify-center p-8">
        {children}
      </div>

      {totalSlides > 1 && (
        <div className="flex justify-center gap-2 pb-6">
          {Array.from({ length: totalSlides }, (_, i) => (
            <div
              key={i}
              className={`h-2 w-2 rounded-full transition-colors ${
                i === slideIndex ? "bg-foreground" : "bg-muted-foreground/30"
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
