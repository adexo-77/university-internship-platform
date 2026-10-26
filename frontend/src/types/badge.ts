export interface BadgeProgress {
  current: number;
  target: number;
}

export interface AchievementBadge {
  id: string;
  title: string;
  description: string;
  earned: boolean;
  progress?: BadgeProgress | null;
}
