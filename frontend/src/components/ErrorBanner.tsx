type ErrorBannerProps = {
  message: string;
};

export function ErrorBanner({ message }: ErrorBannerProps) {
  return (
    <p className="rounded-lg border border-rose-400/20 bg-rose-400/5 px-4 py-3 text-sm text-rose-300/90">
      {message}
    </p>
  );
}
