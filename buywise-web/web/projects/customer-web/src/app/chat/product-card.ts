import { CurrencyPipe, DatePipe } from '@angular/common';
import { Component, input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import type { BlockProductCardPayload } from '../../../../shared/contracts/generated/chat-events';

/** block.product_card (ADR-024). Image is a placeholder (ADR-033). */
@Component({
  selector: 'bw-product-card',
  imports: [MatCardModule, CurrencyPipe, DatePipe],
  template: `
    <mat-card appearance="outlined" class="card">
      <div class="image" aria-hidden="true">{{ card().model.charAt(0) }}</div>
      <div class="body">
        <div class="model">{{ card().model }}</div>
        @if (card().listPrice) { <div class="price">from {{ card().listPrice | currency: 'USD' }}</div> }
        @switch (card().availability) {
          @case ('preorder') { <div class="badge pre">Pre-order @if (card().shipsOn) { · ships {{ card().shipsOn | date }} }</div> }
          @case ('discontinued') { <div class="badge off">Discontinued</div> }
        }
        @if (card().stockAtStore; as s) {
          <div class="stock" [class.out]="s.quantity === 0">
            {{ s.quantity > 0 ? s.quantity + ' in stock' : 'Out of stock' }} at {{ s.storeName }}
          </div>
        }
      </div>
    </mat-card>`,
  styles: `
    .card { display: flex; flex-direction: row; gap: 12px; padding: 12px; max-width: 360px; }
    .image { width: 56px; height: 56px; border-radius: 12px; display: grid; place-items: center; font-size: 24px;
             background: var(--mat-sys-secondary-container); color: var(--mat-sys-on-secondary-container); flex: none; }
    .model { font-weight: 600; }
    .price { color: var(--mat-sys-on-surface-variant); }
    .stock { color: var(--mat-sys-primary); margin-top: 4px; }
    .stock.out, .badge.off { color: var(--mat-sys-error); }
    .badge { font-size: 0.85em; margin-top: 4px; }`,
})
export class ProductCard {
  readonly card = input.required<BlockProductCardPayload>();
}
