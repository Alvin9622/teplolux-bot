import { OperatorSummaryBuilder } from './operator-summary.builder';
import { OperatorSummaryInput } from './operator-summary.types';

describe('OperatorSummaryBuilder', () => {
  const builder = new OperatorSummaryBuilder();
  const when = new Date('2026-01-02T03:04:05.000Z');

  const productInput: OperatorSummaryInput = {
    requestType: 'PRICE_REQUEST',
    productCategory: 'BOILERS',
    fullName: '  Vasil Sodiqov  ',
    phone: ' +998901234567 ',
    city: ' Tashkent ',
    customerMessage: '  Do you deliver?  ',
    language: 'uz',
    requestTime: when,
  };

  it('builds a structured summary and normalises values', () => {
    const summary = builder.build(productInput);

    expect(summary).toEqual({
      requestType: 'PRICE_REQUEST',
      selectedProduct: 'BOILERS',
      customerName: 'Vasil Sodiqov',
      phone: '+998901234567',
      city: 'Tashkent',
      customerMessage: 'Do you deliver?',
      requestTime: when.toISOString(),
      language: 'uz',
    });
  });

  it('omits optional product and message when absent/empty', () => {
    const summary = builder.build({
      requestType: 'SERVICE_REQUEST',
      fullName: 'Ali',
      phone: '+998900000000',
      city: 'Samarkand',
      customerMessage: '   ',
      language: 'ru',
      requestTime: when,
    });

    expect(summary.selectedProduct).toBeUndefined();
    expect(summary.customerMessage).toBeUndefined();
  });

  it('defaults request time to now when not provided', () => {
    const before = Date.now();
    const summary = builder.build({
      requestType: 'OPERATOR_REQUEST',
      fullName: 'A',
      phone: '+1',
      city: 'B',
      language: 'uz',
    });
    expect(new Date(summary.requestTime).getTime()).toBeGreaterThanOrEqual(before);
  });

  it('formats a readable operator block with every field', () => {
    const text = builder.format(builder.build(productInput));

    expect(text).toContain('📩 New Customer Request');
    expect(text).toContain('Request Type: PRICE_REQUEST');
    expect(text).toContain('Selected Product: BOILERS');
    expect(text).toContain('Customer Name: Vasil Sodiqov');
    expect(text).toContain('Phone: +998901234567');
    expect(text).toContain('City: Tashkent');
    expect(text).toContain('Customer Message: Do you deliver?');
    expect(text).toContain(`Request Time: ${when.toISOString()}`);
    expect(text).toContain('Language: uz');
  });

  it('hides optional lines in the formatted block when not present', () => {
    const text = builder.format(
      builder.build({
        requestType: 'DEALER_REQUEST',
        fullName: 'Ali',
        phone: '+998900000000',
        city: 'Bukhara',
        language: 'ru',
        requestTime: when,
      }),
    );

    expect(text).not.toContain('Selected Product:');
    expect(text).not.toContain('Customer Message:');
    expect(text).toContain('Request Type: DEALER_REQUEST');
  });
});
