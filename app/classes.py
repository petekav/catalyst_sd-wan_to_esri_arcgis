class Csm:
  def __init__(self, url, username, password):
    self.url = url
    self.username = username
    self.password = password
  def __str__(self):
    return f"{self.url},{self.username},{self.password}"


class MqttBroker:
  def __init__(self, url, port, tls, username, password):
    self.url = url
    self.port = port
    self.tls = tls
    self.username = username
    self.password = password
  def __str__(self):
    return f"{self.url} on port {self.port}, with TLS set to {self.tls}"