import {
  Entity,
  PrimaryColumn,
  Column,
} from 'typeorm';

@Entity({ schema: 'mart', name: 'sales' })
export class MartSale {
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

  @Column({ name: 'total_amount', type: 'numeric', precision: 14, scale: 2 })
  totalAmount: number;
}