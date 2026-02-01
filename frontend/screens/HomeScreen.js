```javascript
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
  RefreshControl,
  Dimensions,
  StatusBar,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const [batteryData, setBatteryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBatteryData();
  }, []);

  const fetchBatteryData = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      // Simulate API call with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch('https://api.evlifemanager.com/api/vehicles/1/battery', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer your-token-here',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Validate data structure
      if (!data || typeof data.soc === 'undefined') {
        throw new Error('Invalid data format received');
      }

      setBatteryData(data);
    } catch (error) {
      console.error('Error fetching battery data:', error);
      setError(error.message);
      
      // Fallback mock data for development
      setBatteryData({
        soc: 85,
        soh: 94,
        temperature: 23,
        health_score: 'Excellent',
        voltage: 400.5,
        current: -15.2,
        estimated_range: 320,
        charging_status: 'Not Charging'
      });
      
      Alert.alert(
        'Connection Error',
        'Unable to fetch real-time data. Showing cached information.',
        [{ text: 'OK' }]
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    fetchBatteryData(true);
  };

  const getBatteryColor = (soc) => {
    if (soc >= 80) return '#4CAF50';
    if (soc >= 50) return '#FF9800';
    if (soc >= 20) return '#FF5722';
    return '#F44336';
  };

  const getHealthScoreColor = (score) => {
    switch (score) {
      case 'Excellent': return '#4CAF50';
      case 'Good': return '#8BC34A';
      case 'Fair': return '#FF9800';
      case 'Poor': return '#FF5722';
      default: return '#9E9E9E';
    }
  };

  if (loading && !batteryData) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <StatusBar barStyle="light-content" backgroundColor="#1E3A8A" />
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading your EV data...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1E3A8A" />
      
      {/* Header with Gradient */}
      <LinearGradient
        colors={['#1E3A8A', '#3B82F6']}
        style={styles.headerGradient}
      >
        <View style={styles.headerContent}>
          <Text style={styles.header}>EV Life Manager</Text>
          <Text style={styles.subHeader}>Your Smart EV Companion</Text>
          <TouchableOpacity 
            style={styles.profileButton}
            onPress={() => navigation.navigate('Profile')}
          >
            <Icon name="account-circle" size={32} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      </LinearGradient>

      <ScrollView 
        style={styles.scrollContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Battery Status Card */}
        <View style={styles.batteryCard}>
          <LinearGradient
            colors={['#FFFFFF', '#F8FAFC']}
            style={styles.cardGradient}
          >
            <View style={styles.batteryHeader}>
              <Icon name="battery" size={28} color={getBatteryColor(batteryData?.soc)} />
              <Text style={styles.cardTitle}>Battery Status</Text>
              <Text style={styles.chargingStatus}>{batteryData?.charging_status}</Text>
            </View>
            
            <View style={styles.batteryMain}>
              <Text style={[styles.batteryValue, { color: getBatteryColor(batteryData?.soc) }]}>
                {batteryData?.soc}%
              </Text>
              <Text style={styles.batteryLabel}>State of Charge</Text>
              
              {/* Battery Level Bar */}
              <View style={styles.batteryBar}>
                <View 
                  style={[
                    styles.batteryFill, 
                    { 
                      width: `${batteryData?.soc}%`,
                      backgroundColor: getBatteryColor(batteryData?.soc)
                    }
                  ]} 
                />
              </View>
              
              <Text style={styles.rangeText}>
                Est. Range: {batteryData?.estimated_range} km
              </Text>
            </View>
          </LinearGradient>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionsContainer}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          
          <TouchableOpacity 
            style={[styles.actionButton, styles.primaryAction]}
            onPress={() => navigation.navigate('BatteryMonitor')}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={['#007AFF', '#0056CC']}
              style={styles.buttonGradient}
            >
              <Icon name="chart-line" size={24} color="#FFFFFF" />
              <View style={styles.buttonTextContainer}>
                <Text style={styles.buttonText}>Battery Monitoring</Text>
                <Text style={styles.buttonSubtext}>Real-time analytics</Text>
              </View>
              <Icon name="chevron-right" size={20} color="#FFFFFF" />
            </LinearGradient>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionButton, styles.secondaryAction]}
            onPress={() => navigation.navigate('ChargingScheduler')}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={['#10B981', '#059669']}
              style={styles.buttonGradient}
            >
              <Icon name="lightning-bolt" size={24} color="#FFFFFF" />
              <View style={styles.buttonTextContainer}>
                <Text style={styles.buttonText}>Smart Charging</Text>
                <Text style={styles.buttonSubtext}>Optimize charging times</Text>
              </View>
              <Icon name="chevron-right" size={20} color="#FFFFFF" />
            </LinearGradient>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionButton, styles.tertiaryAction]}
            onPress={() => navigation.navigate('ServiceCenters')}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={['#F59E0B', '#D97706']}
              style={styles.buttonGradient}
            >
              <Icon name="wrench" size={24} color="#FFFFFF" />
              <View style={styles.buttonTextContainer}>
                <Text style={styles.buttonText}>Service Centers</Text>
                <Text style={styles.buttonSubtext}>Find nearby services</Text>
              </View>
              <Icon name="chevron-right" size={20} color="#FFFFFF" />
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* Statistics Grid */}
        <View style={styles.statsContainer}>
          <Text style={styles.sectionTitle}>Vehicle Health</Text>
          
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Icon name="heart-pulse" size={24} color="#4CAF50" />
              <Text style={styles.statLabel}>State of Health</Text>
              <Text style={styles.statValue}>{batteryData?.soh}%</Text>
              <View style={[styles.statIndicator, { backgroundColor: '#4CAF50' }]} />
            </View>
            
            <View style={styles.statCard}>
              <Icon name="thermometer" size={24} color="#FF9800" />
              <Text style={styles.statLabel}>Temperature</Text>
              <Text style={styles.statValue}>{batteryData?.temperature}°C</Text>
              <View style={[styles.statIndicator, { backgroundColor: '#FF9800' }]} />
            </View>
            
            <View style={styles.statCard}>
              <Icon name="shield-check" size={24} color={getHealthScoreColor(batteryData?.health_score)} />
              <Text style={styles.statLabel}>Health Score</Text>
              <Text style={[styles.statValue, { fontSize: 14 }]}>{batteryData?.health_score}</Text>
              <View style={[styles.statIndicator, { backgroundColor: getHealthScoreColor(batteryData?.health_score) }]} />
            </View>
            
            <View style={styles.statCard}>
              <Icon name="flash" size={24} color="#9C27B0" />
              <Text style={styles.statLabel}>Voltage</Text>
              <Text style={styles.statValue}>{batteryData?.voltage}V</Text>
              <View style={[styles.statIndicator, { backgroundColor: '#9C27B0' }]} />
            </View>
          </View>
        </View>

        {/* Error Display */}
        {error && (
          <View style={styles.errorContainer}>
            <Icon name="alert-circle" size={24} color="#F44336" />
            <Text style={styles.errorText}>Connection Issue</Text>
            <TouchableOpacity onPress={() => fetchBatteryData()} style={styles.retryButton}>
              <Text style={styles.retryText}>Retry</Text>
            </TouchableOpacity>
          </View>
        )}
        
        <View style={styles.bottomSpacing} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F1F5F9',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1E3A8A',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#FFFFFF',
  },
  headerGradient: {
    paddingBottom: 20,
  },
  headerContent: {
    paddingHorizontal: 20,
    paddingTop: 20,
    position: 'relative',
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
  },
  subHeader: {
    fontSize: 16,
    color: '#E2E8F0',
    textAlign: 'center',
    marginTop: 4,
  },
  profileButton: {
    position: 'absolute',
    top: 20,
    right: 20,
  },
  scrollContainer: {
    flex: 1,
    marginTop: -10,
  },
  batteryCard: {
    margin: 20,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 12,
    elevation: 8,
  },
  cardGradient: {
    padding: 24,
    borderRadius: 20,
  },
  batteryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1E293B',
    marginLeft: 12,
    flex: 1,
  },
  chargingStatus: {
    fontSize: 14,
    color: '#64748B',
    fontWeight: '500',
  },
  batteryMain: {
    alignItems: 'center',
  },
  batteryValue: {
    fontSize: 56,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  batteryLabel: {
    fontSize: 16,
    color: '#64748B',
    marginBottom: 20,
  },
  batteryBar: {
    width: '100%',
    height: 8,
    backgroundColor: '#E2E8F0',
    borderRadius: 4,
    marginBottom: 16,
    overflow: 'hidden',
  },
  batteryFill: {
    height: '100%',
    borderRadius: 4,
  },
  rangeText: {
    fontSize: 16,
    color: '#475569',
    fontWeight: '500',
  },
  actionsContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 16,
  },
  actionButton: {
    marginBottom: 12,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 8,
    elevation: 4,
  },
  buttonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderRadius: 16,
  },
  buttonTextContainer: {
    flex: 1,
    marginLeft: 16,
  },
  buttonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  buttonSubtext: {
    fontSize: 14,
    color: '#E2E8F0',
    marginTop: 2,
  },
  statsContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: (width - 60) / 2,
    backgroundColor: '#