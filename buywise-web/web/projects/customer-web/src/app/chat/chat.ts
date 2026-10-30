import { Component, ElementRef, effect, inject, signal, viewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { marked } from 'marked';
import { ChatStore } from './chat.store';
import { ProductCard } from './product-card';

const SUGGESTIONS = [
  'Is the iPhone 18 Pro in stock at the Austin store?',
  'How long will the store hold my pickup order?',
  'Where is my latest order?',
];

@Component({
  selector: 'bw-chat',
  imports: [FormsModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatProgressBarModule, ProductCard],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat {
  protected readonly store = inject(ChatStore);
  protected readonly draft = signal('');
  protected readonly suggestions = SUGGESTIONS;
  private readonly list = viewChild<ElementRef<HTMLElement>>('list');

  constructor() {
    // keep the newest message in view while text streams in
    effect(() => {
      this.store.items();
      this.store.status();
      queueMicrotask(() => {
        const el = this.list()?.nativeElement;
        if (el) el.scrollTop = el.scrollHeight;
      });
    });
  }

  protected markdown(text: string): string {
    return marked.parse(text, { async: false }) as string; // [innerHTML] sanitizes it (no raw HTML)
  }

  protected submit(text = this.draft()) {
    const value = text.trim();
    if (!value || this.store.sending()) return;
    this.draft.set('');
    this.store.send(value);
  }

  protected onKey(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.submit();
    }
  }
}
