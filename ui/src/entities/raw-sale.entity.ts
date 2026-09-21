import {
  Entity,
  PrimaryColumn,
  Column,
  CreateDateColumn,
  Index,
} from 'typeorm';

@Entity({ schema: 'raw', name: 'sales' })
export class RawSale {
  @PrimaryColumn({ name: 'transaction_id', length: 50 })
  transactionId: string;

  @Column({ name: 'transaction_date', type: 'date' })
  transactionDate: Date;

  @Column({ name: 'customer_id', length: 50 })
  customerId: string;

  @Column({ name: 'product_id', length: 50 })
  productId: string;

  @Column({ type: 'int' })
  quantity: number;

  @Column({ name: 'unit_price', type: 'numeric', precision: 12, scale: 2 })
  unitPrice: number;

  @CreateDateColumn({ name: 'loaded_at' })
  loadedAt: Date;
}