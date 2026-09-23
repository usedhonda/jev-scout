struct NotificationItem {
    let appID: String
    let receivedAt: Double
    let text: String?
}
func newestFirst(_ items: [NotificationItem]) -> [NotificationItem] {
    items.sorted { $0.receivedAt > $1.receivedAt }
}
