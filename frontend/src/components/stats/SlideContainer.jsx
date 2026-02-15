export default function SlideContainer({
  slideIndex,
  totalSlides,
  isPaused,
  progress,
  showPlayerPicker,
  playerList,
  onSelectPlayer,
  onClosePicker,
  children,
}) {
  return (
    <div className="fixed inset-0 flex flex-col bg-background text-foreground">
      {/* Paused badge */}
      {isPaused && !showPlayerPicker && (
        <div className="absolute top-4 right-4 z-10 flex items-center gap-2 rounded-md bg-muted/80 px-3 py-1.5 text-sm text-muted-foreground backdrop-blur animate-pulse">
          <span>⏸</span>
          <span>Paused</span>
        </div>
      )}

      {/* Player picker overlay */}
      {showPlayerPicker && (
        <div
          className="absolute inset-0 z-20 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={onClosePicker}
        >
          <div
            className="w-full max-w-md rounded-lg bg-background p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="mb-4 text-center text-lg font-semibold">
              Select Player
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {playerList?.map((p) => (
                <button
                  key={p.id}
                  onClick={() => onSelectPlayer(p.id)}
                  className="rounded-md border border-border px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
                >
                  {p.name}
                </button>
              ))}
            </div>
            <p className="mt-4 text-center text-xs text-muted-foreground">
              Press <kbd className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px]">P</kbd> or <kbd className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px]">Esc</kbd> to close
            </p>
          </div>
        </div>
      )}

      <div className="flex flex-1 items-center justify-center p-8">
        {children}
      </div>

      {totalSlides > 1 && (
        <div className="flex flex-col items-center gap-3 pb-6">
          {/* Progress bar */}
          <div className="h-1 w-48 overflow-hidden rounded-full bg-muted-foreground/20">
            <div
              className="h-full rounded-full bg-foreground/60 transition-[width] duration-100 ease-linear"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Dot indicators */}
          <div className="flex justify-center gap-2">
            {Array.from({ length: totalSlides }, (_, i) => (
              <div
                key={i}
                className={`h-2 w-2 rounded-full transition-colors ${
                  i === slideIndex ? "bg-foreground" : "bg-muted-foreground/30"
                }`}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
