export interface User {
  id: string;
  email: string;
  name: string;
  timezone: string;
  created_at: string;
  preferences: Record<string, any>;
  telegram_verified: boolean;
}

export interface Meeting {
  id: string;
  user_id: string;
  event_id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  attendees: Attendee[];
  meeting_link?: string;
  meeting_platform: string;
  context_generated: boolean;
  is_confirmed: boolean;
  notes?: string;
  created_at: string;
}

export interface Attendee {
  email: string;
  name?: string;
}

export interface Context {
  id: string;
  meeting_id: string;
  ai_brief: string;
  meeting_type: string;
  key_topics: string[];
  preparation_checklist: ChecklistItem[];
  attendee_context: Record<string, string>;
  generated_at: string;
  ai_model_version: string;
  user_edited: boolean;
}

export interface ChecklistItem {
  id?: string;
  text: string;
  completed: boolean;
}

export interface Notification {
  id: string;
  meeting_id: string;
  channel: "email" | "telegram" | "whatsapp";
  scheduled_time: string;
  status: "scheduled" | "sent" | "delivered" | "failed";
  sent_time?: string;
  delivered_time?: string;
}

export interface UserPreferences {
  notification_email: boolean;
  notification_telegram: boolean;
  notification_whatsapp: boolean;
  reminder_timing: number[];
  do_not_disturb_start: string;
  do_not_disturb_end: string;
  monitored_calendars: string[];
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}
