import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Base/Header';
import PostListContainer from './components/Post/PostListContainer';
import PostDetailContainer from './components/Post/PostDetailContainer';
import Footer from './components/Base/Footer';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import ProtectedRoute from './components/Base/ProtectedRoute';
import Profile from './components/User/Profile';
import UserProfileContainer from './components/User/UserProfileContainer';
import CreatePost from './components/Post/CreatePost';

function App() {
  return (
      <Router>
          <div>
              <Header />
              <Routes>
                  <Route exact path="/" element={
                    <ProtectedRoute>
                      <PostListContainer />
                    </ProtectedRoute>
                  }
                  />
                  <Route path="/posts/:id" element={
                    <ProtectedRoute>
                      <PostDetailContainer />
                    </ProtectedRoute>
                  }
                  />
                  <Route
                    path="/profile"
                    element={
                        <ProtectedRoute>
                            <Profile />
                        </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/users/:userId"
                    element={
                        <ProtectedRoute>
                            <UserProfileContainer />
                        </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/posts"
                    element={
                        <ProtectedRoute>
                            <CreatePost />
                        </ProtectedRoute>
                    }
                  />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route
                      path="/protected" // Route yêu cầu xác thực
                      element={
                          <ProtectedRoute>
                              <div>Protected Content</div>
                          </ProtectedRoute>
                      }
                  />
              </Routes>
              <Footer />
          </div>
      </Router>
  );
}

export default App;