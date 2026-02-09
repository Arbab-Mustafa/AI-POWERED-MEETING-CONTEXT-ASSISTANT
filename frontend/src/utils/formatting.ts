export function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function getTimeUntilMeeting(startTime: string): string {
  const now = new Date();
  const start = new Date(startTime);
  const diffMs = start.getTime() - now.getTime();

  if (diffMs < 0) return "Meeting in progress or past";

  const minutes = Math.floor(diffMs / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d away`;
  if (hours > 0) return `${hours}h away`;
  return `${minutes}m away`;
}

export function truncate(text: string, length: number = 100): string {
  return text.length > length ? text.slice(0, length) + "..." : text;
}

export function classNames(...classes: (string | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}
