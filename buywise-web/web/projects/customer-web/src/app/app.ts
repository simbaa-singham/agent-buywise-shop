import { Component, inject, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Chat } from './chat/chat';
import { ChatStore } from './chat/chat.store';

@Component({
  selector: 'app-root',
  imports: [MatToolbarModule, MatButtonModule, Chat],
  template: `
    <mat-toolbar class="bar">
      <span class="brand">BuyWise</span>
      <span class="spacer"></span>
      <button mat-button type="button" (click)="store.newChat()">New chat</button>
      @if (store.loggedIn()) {
        <span class="who">{{ store.name() }}</span>
        <a mat-stroked-button href="/api/auth/logout">Log out</a>
      } @else {
        <a mat-flat-button href="/api/auth/login">Log in</a>
      }
    </mat-toolbar>
    <main class="main"><bw-chat /></main>`,
  styles: `
    :host { display: flex; flex-direction: column; height: 100dvh; }
    .bar { gap: 8px; background: var(--mat-sys-surface-container); }
    .brand { font-weight: 700; }
    .spacer { flex: 1; }
    .who { font: var(--mat-sys-body-medium); }
    .main { flex: 1; display: flex; min-height: 0; }`,
})
export class App implements OnInit {
  protected readonly store = inject(ChatStore);

  ngOnInit() {
    this.store.init();
  }
}
