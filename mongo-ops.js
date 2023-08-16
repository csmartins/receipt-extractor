db.receipts.find({})
db.products.find({})
db.getCollection("receipts").find({_id: ObjectId("635dc96aa2145ed780704a55")})

db.receipts.find({url: 'http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode?p=33210531487473012103650020000035461870027213|2|1|2|976181ee8ae063994e3b2cbe76ef387838fc9e4f'})

db.receipts.find({store: 'HORTIGIL HORTIFRUTI S/A'})
db.receipts.update(
  { _id: ObjectId("635dc96aa2145ed780704a55") },
  {
    $set: {
      products: []
    }
  }
)

db.receipts.update(
  { _id: ObjectId("635dc96aa2145ed780704a55") },
  {
    $set: {
      products: [
      {
        product_id: ObjectId("637ad55ec8df68e9e6465e83"),
        product_quantity: '0,17',
        unity_type: 'kg',
        total_value: '6,80'
      },
      {
        product_id: ObjectId("637ad563c8df68e9e6465e87"),
        product_quantity: '1',
        unity_type: 'UN',
        total_value: '9,99'
      },
      {
        product_id: ObjectId("637ad569c8df68e9e6465e8b"),
        product_quantity: '0,374',
        unity_type: 'kg',
        total_value: '18,66'
      },
      {
        product_id: ObjectId("637ad570c8df68e9e6465e8f"),
        product_quantity: '0,25',
        unity_type: 'kg',
        total_value: '6,25'
      },
      {
        product_id: ObjectId("637ad570c8df68e9e6465e8f"),
        product_quantity: '0,266',
        unity_type: 'kg',
        total_value: '6,65'
      }
    ]
    }
  }
)