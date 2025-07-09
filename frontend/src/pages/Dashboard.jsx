import React, { useEffect, useState } from 'react'
import axios from 'axios'

export default function Dashboard() {
  const [status, setStatus] = useState({ carts: [] })
  const [loading, setLoading] = useState(false)

  const fetchStatus = async () => {
    const res = await axios.get('/status')
    setStatus(res.data)
  }

  const startAgent = async () => {
    setLoading(true)
    await axios.post('/start')
    await fetchStatus()
    setLoading(false)
  }

  useEffect(() => {
    fetchStatus()
  }, [])

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Order Recovery Dashboard</h1>
        <button
          onClick={startAgent}
          className="bg-blue-500 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          {loading ? 'Running...' : 'Run Agent'}
        </button>
      </div>

      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th className="px-4 py-2">Cart ID</th>
            <th className="px-4 py-2">Emails Sent</th>
            <th className="px-4 py-2">Recovered?</th>
          </tr>
        </thead>
        <tbody>
          {status.carts && status.carts.map(cart => (
            <tr key={cart.id} className="text-center border-t">
              <td className="px-4 py-2">{cart.id}</td>
              <td className="px-4 py-2">
                {cart.email_sent.map((e, idx) => (
                  <div key={idx}>{e.discount}% at {new Date(e.time).toLocaleString()}</div>
                ))}
              </td>
              <td className="px-4 py-2">{cart.recovered ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
