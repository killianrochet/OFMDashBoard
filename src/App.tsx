import React, { useState, useEffect } from 'react';
import { Smartphone, Clock, RefreshCw } from 'lucide-react';
import AdminDashboard from './pages/AdminDashboard';

interface Device {
  id: number;
  name: string;
  model: string;
  status: string;
  created_at: string;
  device_id: string;
  platform_version: string;
  accounts: string[];
}

interface Post {
  id: number;
  device_id: number;
  scheduled_time: string;
  media_path: string;
  caption: string;
  post_type: string;
  status: string;
  created_at: string;
  account?: string;
}

function App() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [accounts, setAccounts] = useState<string[]>([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [posts, setPosts] = useState<Post[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [newPost, setNewPost] = useState({
    device_id: '',
    scheduled_time: '',
    caption: '',
    post_type: 'photo'
  });
  const [activePage, setActivePage] = useState<'main' | 'admin'>('main');

  const fetchDevices = async () => {
    try {
      const response = await fetch('http://localhost:5000/devices');
      const data = await response.json();
      setDevices(data);
    } catch (error) {
      console.error('Error fetching devices:', error);
    }
  };

  const scanDevices = async () => {
    try {
      await fetch('http://localhost:5000/devices/scan', { method: 'POST' });
      fetchDevices();
    } catch (error) {
      console.error('Error scanning devices:', error);
    }
  };

  const fetchPosts = async () => {
    try {
      const response = await fetch('http://localhost:5000/posts');
      const data = await response.json();
      setPosts(data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
  };

  const handleSubmit = async () => {
    try {
      if (!selectedFile || !newPost.device_id || !newPost.scheduled_time || !newPost.caption || !selectedAccount) {
        alert("Tous les champs doivent être remplis.");
        return;
      }

      const uploadData = new FormData();
      uploadData.append('file', selectedFile);
      uploadData.append('device_id', newPost.device_id);

      const uploadRes = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: uploadData
      });

      const uploadJson = await uploadRes.json();
      const device_path = uploadJson.device_path;

      const res = await fetch('http://localhost:5000/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...newPost,
          media_path: device_path,
          account: selectedAccount
        })
      });

      const json = await res.json();
      alert('✅ Post planifié avec succès');

      setSelectedFile(null);
      setSelectedAccount('');
      setNewPost({ device_id: '', scheduled_time: '', caption: '', post_type: 'photo' });
      fetchPosts();

    } catch (err) {
      console.error('❌ Erreur lors de la planification :', err);
      alert('Erreur lors de la planification');
    }
  };

  useEffect(() => {
    fetchDevices();
    fetchPosts();
  }, []);

  useEffect(() => {
    const selectedDevice = devices.find(d => d.device_id === newPost.device_id);
    setAccounts(selectedDevice?.accounts || []);
  }, [newPost.device_id, devices]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Instagram Automation Manager</h1>
          <p className="text-gray-600">Gérez vos appareils et planifiez vos posts Instagram</p>
          <div className="mt-4 text-right">
            <button
              onClick={() => setActivePage(activePage === 'main' ? 'admin' : 'main')}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              {activePage === 'main' ? 'Voir le tableau admin' : 'Retour'}
            </button>
          </div>
        </header>

        {activePage === 'main' ? (
          <>
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
                  <Smartphone className="w-5 h-5" /> Appareils connectés
                </h2>
                <button
                  onClick={scanDevices}
                  className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
                >
                  <RefreshCw className="w-4 h-4" /> Scanner
                </button>
              </div>

              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-2 text-left">Nom</th>
                    <th className="px-4 py-2 text-left">Modèle</th>
                    <th className="px-4 py-2 text-left">Version Android</th>
                    <th className="px-4 py-2 text-left">Statut</th>
                    <th className="px-4 py-2 text-left">ID Appareil</th>
                  </tr>
                </thead>
                <tbody>
                  {devices.map((device) => (
                    <tr key={device.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2">{device.name}</td>
                      <td className="px-4 py-2">{device.model}</td>
                      <td className="px-4 py-2">{device.platform_version}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded-full text-sm ${device.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                          {device.status}
                        </span>
                      </td>
                      <td className="px-4 py-2">{device.device_id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5" /> Planifier un nouveau post
              </h2>

              <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <select
                    className="px-4 py-2 border rounded-md"
                    value={newPost.device_id}
                    onChange={(e) => setNewPost({ ...newPost, device_id: e.target.value })}
                    required
                  >
                    <option value="">Sélectionner un appareil</option>
                    {devices.map((device) => (
                      <option key={device.device_id} value={device.device_id}>
                        {device.name} ({device.model})
                      </option>
                    ))}
                  </select>

                  <select
                    className="px-4 py-2 border rounded-md"
                    value={selectedAccount}
                    onChange={(e) => setSelectedAccount(e.target.value)}
                    required
                  >
                    <option value="">Sélectionner un compte Instagram</option>
                    {accounts.map((acc) => (
                      <option key={acc} value={acc}>{acc}</option>
                    ))}
                  </select>

                  <input
                    type="datetime-local"
                    className="px-4 py-2 border rounded-md"
                    value={newPost.scheduled_time}
                    onChange={(e) => setNewPost({ ...newPost, scheduled_time: e.target.value })}
                    required
                  />

                  <select
                    className="px-4 py-2 border rounded-md"
                    value={newPost.post_type}
                    onChange={(e) => setNewPost({ ...newPost, post_type: e.target.value })}
                    required
                  >
                    <option value="photo">Photo</option>
                    <option value="reel">Reel</option>
                  </select>

                  <input
                    type="file"
                    accept={newPost.post_type === 'photo' ? 'image/*' : 'video/*'}
                    className="px-4 py-2 border rounded-md"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    required
                  />

                  <textarea
                    className="md:col-span-2 px-4 py-2 border rounded-md"
                    placeholder="Description du post..."
                    value={newPost.caption}
                    onChange={(e) => setNewPost({ ...newPost, caption: e.target.value })}
                    required
                    rows={4}
                  />
                </div>

                <button
                  type="submit"
                  className="w-full bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700"
                >
                  Planifier le post
                </button>
              </form>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 mt-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Posts planifiés</h2>
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-2 text-left">Appareil</th>
                    <th className="px-4 py-2 text-left">Type</th>
                    <th className="px-4 py-2 text-left">Heure prévue</th>
                    <th className="px-4 py-2 text-left">Compte</th>
                    <th className="px-4 py-2 text-left">Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {posts.map((post) => (
                    <tr key={post.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2">
                        {devices.find(d => d.id === post.device_id)?.name || 'Unknown'}
                      </td>
                      <td className="px-4 py-2">{post.post_type}</td>
                      <td className="px-4 py-2">{new Date(post.scheduled_time).toLocaleString()}</td>
                      <td className="px-4 py-2">{post.account || '-'}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded-full text-sm ${post.status === 'completed' ? 'bg-green-100 text-green-800' : post.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                          {post.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <AdminDashboard />
        )}
      </div>
    </div>
  );
}

export default App;
